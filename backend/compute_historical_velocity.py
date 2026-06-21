import pandas as pd
import numpy as np
import joblib
from pyiceberg.catalog import load_catalog
from cost_model import assign_segment, decide_transaction, VELOCITY_REVIEW_THRESHOLD

BUCKET_NAME = "riskflow-lakehouse-7d75d72b"

print("Loading data and model...")
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

print("Recomputing historical 1-hour velocity per card (this is the slow part)...")
df = df.sort_values(["card1", "txn_timestamp"]).reset_index(drop=True)
df["txn_timestamp"] = pd.to_datetime(df["txn_timestamp"])

# For each card, count how many of its OWN prior transactions fall within
# the 1 hour before the current one — same windowing logic as the live
# Kafka consumer (feature_consumer.py), computed retroactively in bulk
# instead of one event at a time.
def rolling_1h_count(group):
    times = group["txn_timestamp"].values
    counts = np.zeros(len(times), dtype=int)
    start = 0
    for i in range(len(times)):
        while times[i] - times[start] > np.timedelta64(1, "h"):
            start += 1
        counts[i] = i - start  # count of prior txns in window, excluding current
    return counts

df["txn_count_1h"] = df.groupby("card1", group_keys=False).apply(
    lambda g: pd.Series(rolling_1h_count(g), index=g.index)
)

print(f"Velocity distribution: mean={df['txn_count_1h'].mean():.2f}, "
      f"max={df['txn_count_1h'].max()}, "
      f"pct over threshold={100*(df['txn_count_1h'] > VELOCITY_REVIEW_THRESHOLD).mean():.2f}%")

df.to_parquet("/tmp/df_with_velocity.parquet")
print("Saved to /tmp/df_with_velocity.parquet for the next script.")
