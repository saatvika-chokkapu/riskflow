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
        return amount
    if is_fraud == 0 and decision == "decline":
        return decline_cost(segment)
    return 0.0

riskflow_decisions = df.apply(
    lambda row: decide_transaction(row["fraud_probability"], row["amount"], row["segment"])[0],
    axis=1
)
df["riskflow_decision"] = riskflow_decisions
df["riskflow_cost"] = [
    realized_cost(label, decision, amt, seg)
    for label, decision, amt, seg in zip(df["is_fraud_label"], riskflow_decisions, df["amount"], df["segment"])
]

naive_decisions = df["fraud_probability"].apply(lambda p: "decline" if p > NAIVE_THRESHOLD else "approve")
df["naive_decision"] = naive_decisions
df["naive_cost"] = [
    realized_cost(label, decision, amt, seg)
    for label, decision, amt, seg in zip(df["is_fraud_label"], naive_decisions, df["amount"], df["segment"])
]

output_cols = [
    "txn_id", "txn_date", "card1", "segment", "amount", "is_fraud_label",
    "fraud_probability", "riskflow_decision", "riskflow_cost",
    "naive_decision", "naive_cost"
]
result_df = df[output_cols].copy()
result_df.columns = [col.upper() for col in result_df.columns]

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

success, num_chunks, num_rows, _ = write_pandas(
    conn,
    result_df,
    table_name="DECISION_RESULTS",
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA"),
    auto_create_table=True,
    overwrite=True,
)
print(f"Success: {success} | Rows loaded: {num_rows}")
conn.close()