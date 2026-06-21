import pandas as pd
import joblib

BUCKET_NAME = "riskflow-lakehouse-7d75d72b"

# Documented assumptions from docs/cost_model_assumptions.md — NOT derived from this dataset
CHURN_RATE_AFTER_FALSE_DECLINE = 0.39

# Documented assumption, not derived from this dataset: more than 5 transactions
# from one card within 1 hour resembles card-testing fraud patterns.
VELOCITY_REVIEW_THRESHOLD = 5

# Estimated lifetime value per segment — a reasonable, documented proxy,
# not real CLV data (the dataset has none). Higher for credit (typically
# higher-spend, more loyal) vs debit customers.
SEGMENT_LIFETIME_VALUE = {
    "credit_high_value": 850,
    "credit_low_value": 400,
    "debit_high_value": 500,
    "debit_low_value": 200,
    "unknown": 300,  # fallback for missing card6 data
}

def assign_segment(row):
    card_type = "credit" if row["card6"] == "credit" else "debit" if row["card6"] == "debit" else "unknown"
    if card_type == "unknown":
        return "unknown"
    value_tier = "high_value" if row["amount"] > 100 else "low_value"
    return f"{card_type}_{value_tier}"

def decline_cost(segment):
    lifetime_value = SEGMENT_LIFETIME_VALUE.get(segment, SEGMENT_LIFETIME_VALUE["unknown"])
    return CHURN_RATE_AFTER_FALSE_DECLINE * lifetime_value

def decide_transaction(fraud_probability, amount, segment, cost_multiplier=1.0):
    """
    Returns (decision, expected_cost_approve, expected_cost_decline)
    decision is one of: 'approve', 'decline'

    cost_multiplier scales the assumed decline_cost (churn rate x lifetime value),
    used for sensitivity analysis — since both inputs are documented assumptions,
    not values derived from this dataset. Default 1.0 reproduces the original logic.
    """
    p_legitimate = 1 - fraud_probability

    cost_of_approving = fraud_probability * amount
    cost_of_declining = p_legitimate * decline_cost(segment) * cost_multiplier

    decision = "decline" if cost_of_declining < cost_of_approving else "approve"
    return decision, cost_of_approving, cost_of_declining


if __name__ == "__main__":
    from pyiceberg.catalog import load_catalog
    model = joblib.load("backend/fraud_model.pkl")

    catalog = load_catalog("riskflow", **{"type": "glue", "warehouse": f"s3://{BUCKET_NAME}/"})
    table = catalog.load_table("riskflow_lakehouse.raw_transactions")
    df = table.scan().to_pandas().copy()

    categorical_cols = ["ProductCD", "card4", "card6", "P_emaildomain", "DeviceType", "DeviceInfo"]
    df_encoded = df.copy()
    for col in categorical_cols:
        df_encoded[col] = df_encoded[col].astype("category").cat.codes

    feature_cols = ["amount", "card1", "addr1"] + categorical_cols
    probs = model.predict_proba(df_encoded[feature_cols])[:, 1]
    df["fraud_probability"] = probs

    # Look at the 10 highest-risk transactions specifically
    top_risk = df.sort_values("fraud_probability", ascending=False).head(10)

    for _, row in top_risk.iterrows():
        segment = assign_segment(row)
        decision, cost_approve, cost_decline = decide_transaction(
            row["fraud_probability"], row["amount"], segment
        )
        print(f"txn_id={row['txn_id']} | amount=${row['amount']:.2f} | segment={segment} | "
              f"P(fraud)={row['fraud_probability']:.4f} | actual_fraud={row['is_fraud_label']} | "
              f"decision={decision} | cost_approve=${cost_approve:.2f} | cost_decline=${cost_decline:.2f}")