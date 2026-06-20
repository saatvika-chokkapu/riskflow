
import pandas as pd
import numpy as np
from pyiceberg.catalog import load_catalog

BUCKET_NAME = "riskflow-lakehouse-7d75d72b"

catalog = load_catalog("riskflow", **{"type": "glue", "warehouse": f"s3://{BUCKET_NAME}/"})
table = catalog.load_table("riskflow_lakehouse.raw_transactions")
df = table.scan().to_pandas()
df["txn_date"] = pd.to_datetime(df["txn_date"])
df = df.sort_values("txn_date")

split_point = df["txn_date"].quantile(0.7)
baseline = df[df["txn_date"] <= split_point]
current = df[df["txn_date"] > split_point]

print(f"Baseline: {len(baseline)} rows | Current: {len(current)} rows")
print(f"Split date: {split_point.date()}")

def calculate_psi(baseline_col, current_col, bins=10):
    breakpoints = np.quantile(baseline_col.dropna(), np.linspace(0, 1, bins + 1))
    breakpoints[0] = -np.inf
    breakpoints[-1] = np.inf

    baseline_counts = pd.cut(baseline_col, breakpoints).value_counts(normalize=True).sort_index()
    current_counts = pd.cut(current_col, breakpoints).value_counts(normalize=True).sort_index()

    baseline_pct = baseline_counts.replace(0, 0.0001)
    current_pct = current_counts.reindex(baseline_pct.index, fill_value=0.0001).replace(0, 0.0001)

    psi = np.sum((current_pct - baseline_pct) * np.log(current_pct / baseline_pct))
    return psi

features = ["amount", "card1", "addr1"]

print("\nDrift Report (PSI per feature):")
for feature in features:
    psi = calculate_psi(baseline[feature], current[feature])
    if psi < 0.1:
        status = "STABLE"
    elif psi < 0.25:
        status = "MODERATE SHIFT"
    else:
        status = "SIGNIFICANT DRIFT"
    print(f"  {feature}: PSI={psi:.4f} [{status}]")
