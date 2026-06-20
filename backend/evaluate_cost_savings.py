import pandas as pd
import joblib
from pyiceberg.catalog import load_catalog
from cost_model import assign_segment, decline_cost, decide_transaction

BUCKET_NAME = "riskflow-lakehouse-7d75d72b"
NAIVE_THRESHOLD = 0.5  # the typical default a tutorial-style classifier would use

model = joblib.load("backend/fraud_model.pkl")

catalog = load_catalog("riskflow", **{"type": "glue", "warehouse": f"s3://{BUCKET_NAME}/"})
table = catalog.load_table("riskflow_lakehouse.raw_transactions")
df = table.scan().to_pandas().copy()

categorical_cols = ["ProductCD", "card4", "card6", "P_emaildomain", "DeviceType", "DeviceInfo"]
df_encoded = df.copy()
for col in categorical_cols:
    df_encoded[col] = df_encoded[col].astype("category").cat.codes

feature_cols = ["amount", "card1", "addr1"] + categorical_cols
df["fraud_probability"] = model.predict_proba(df_encoded[feature_cols])[:, 1]
df["segment"] = df.apply(assign_segment, axis=1)

def realized_cost(is_fraud, decision, amount, segment):
    if is_fraud == 1 and decision == "approve":
        return amount  # fraud got through — real loss
    if is_fraud == 0 and decision == "decline":
        return decline_cost(segment)  # legitimate customer wrongly declined
    return 0.0  # correct decision either way

# --- Strategy 1: RiskFlow's cost-aware decisioning ---
riskflow_decisions = df.apply(
    lambda row: decide_transaction(row["fraud_probability"], row["amount"], row["segment"])[0],
    axis=1
)
df["riskflow_cost"] = [
    realized_cost(label, decision, amt, seg)
    for label, decision, amt, seg in zip(df["is_fraud_label"], riskflow_decisions, df["amount"], df["segment"])
]

# --- Strategy 2: naive fixed-threshold baseline ---
naive_decisions = df["fraud_probability"].apply(lambda p: "decline" if p > NAIVE_THRESHOLD else "approve")
df["naive_cost"] = [
    realized_cost(label, decision, amt, seg)
    for label, decision, amt, seg in zip(df["is_fraud_label"], naive_decisions, df["amount"], df["segment"])
]

# --- Aggregate results ---
riskflow_total = df["riskflow_cost"].sum()
naive_total = df["naive_cost"].sum()

riskflow_fraud_caught = ((df["is_fraud_label"] == 1) & (riskflow_decisions == "decline")).sum()
riskflow_false_declines = ((df["is_fraud_label"] == 0) & (riskflow_decisions == "decline")).sum()

naive_fraud_caught = ((df["is_fraud_label"] == 1) & (naive_decisions == "decline")).sum()
naive_false_declines = ((df["is_fraud_label"] == 0) & (naive_decisions == "decline")).sum()

print("=== RiskFlow Cost-Aware Strategy ===")
print(f"Fraud caught: {riskflow_fraud_caught} | False declines: {riskflow_false_declines}")
print(f"Total realized cost: ${riskflow_total:,.2f}")

print("\n=== Naive Fixed-Threshold (>0.5) Strategy ===")
print(f"Fraud caught: {naive_fraud_caught} | False declines: {naive_false_declines}")
print(f"Total realized cost: ${naive_total:,.2f}")

savings = naive_total - riskflow_total
pct_improvement = (savings / naive_total) * 100
print(f"\n=== Net Improvement ===")
# Prove the mechanism: is RiskFlow catching higher-value fraud on average?
riskflow_caught_amounts = df[(df["is_fraud_label"] == 1) & (riskflow_decisions == "decline")]["amount"]
naive_caught_amounts = df[(df["is_fraud_label"] == 1) & (naive_decisions == "decline")]["amount"]

riskflow_missed_amounts = df[(df["is_fraud_label"] == 1) & (riskflow_decisions == "approve")]["amount"]
naive_missed_amounts = df[(df["is_fraud_label"] == 1) & (naive_decisions == "approve")]["amount"]

print("\n=== Mechanism Check: average $ amount, fraud caught vs missed ===")
print(f"RiskFlow — avg caught: ${riskflow_caught_amounts.mean():.2f} | avg missed: ${riskflow_missed_amounts.mean():.2f}")
print(f"Naive    — avg caught: ${naive_caught_amounts.mean():.2f} | avg missed: ${naive_missed_amounts.mean():.2f}")
print(f"RiskFlow saves: ${savings:,.2f} ({pct_improvement:.1f}% lower total cost)")