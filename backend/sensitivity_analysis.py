import os
import pandas as pd
import joblib
from dotenv import load_dotenv
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from pyiceberg.catalog import load_catalog
from cost_model import assign_segment, decline_cost, decide_transaction

load_dotenv()

BUCKET_NAME = "riskflow-lakehouse-7d75d72b"
NAIVE_THRESHOLD = 0.5

# Documented assumption: the actual churn rate and lifetime-value figures could
# reasonably be wrong by half or double in either direction. This sweep shows
# how much that uncertainty actually matters to the bottom-line result.
MULTIPLIERS = [0.25, 0.5, 1.0, 1.5, 2.0]

print("Loading model and data...")
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

def realized_cost(is_fraud, decision, amount, segment, multiplier):
    if is_fraud == 1 and decision == "approve":
        return amount
    if is_fraud == 0 and decision == "decline":
        return decline_cost(segment) * multiplier
    return 0.0

# Naive baseline doesn't depend on the cost assumption at all — it's a fixed
# probability threshold, so it stays constant across every multiplier.
naive_decisions = df["fraud_probability"].apply(lambda p: "decline" if p > NAIVE_THRESHOLD else "approve")
naive_total_cost = sum(
    realized_cost(label, decision, amt, seg, 1.0)
    for label, decision, amt, seg in zip(df["is_fraud_label"], naive_decisions, df["amount"], df["segment"])
)

results = []
for mult in MULTIPLIERS:
    print(f"Running multiplier {mult}x...")
    decisions = df.apply(
        lambda row: decide_transaction(row["fraud_probability"], row["amount"], row["segment"], mult)[0],
        axis=1
    )
    total_cost = sum(
        realized_cost(label, decision, amt, seg, mult)
        for label, decision, amt, seg in zip(df["is_fraud_label"], decisions, df["amount"], df["segment"])
    )
    fraud_caught = ((df["is_fraud_label"] == 1) & (decisions == "decline")).sum()
    false_declines = ((df["is_fraud_label"] == 0) & (decisions == "decline")).sum()
    savings = naive_total_cost - total_cost

    results.append({
        "cost_multiplier": mult,
        "riskflow_total_cost": round(total_cost, 2),
        "naive_total_cost": round(naive_total_cost, 2),
        "savings_vs_naive": round(savings, 2),
        "savings_pct": round((savings / naive_total_cost) * 100, 2),
        "fraud_caught_count": int(fraud_caught),
        "false_declines_count": int(false_declines),
    })
    print(f"  -> savings: ${savings:,.2f} ({(savings/naive_total_cost)*100:.1f}%)")

result_df = pd.DataFrame(results)
print("\nFull sensitivity results:")
print(result_df.to_string(index=False))

# Push to Snowflake
conn = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    role="ACCOUNTADMIN",
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA"),
)
cursor = conn.cursor()
cursor.execute(f"USE WAREHOUSE {os.getenv('SNOWFLAKE_WAREHOUSE')}")
cursor.execute(f"USE DATABASE {os.getenv('SNOWFLAKE_DATABASE')}")
cursor.execute(f"USE SCHEMA {os.getenv('SNOWFLAKE_SCHEMA')}")

result_df.columns = [c.upper() for c in result_df.columns]
success, num_chunks, num_rows, _ = write_pandas(
    conn, result_df, table_name="SENSITIVITY_RESULTS",
    database=os.getenv("SNOWFLAKE_DATABASE"), schema=os.getenv("SNOWFLAKE_SCHEMA"),
    auto_create_table=True, overwrite=True,
)
print(f"\nLoaded to Snowflake: {success} | Rows: {num_rows}")
conn.close()
