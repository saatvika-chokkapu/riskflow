import pandas as pd
import pyarrow as pa
from datetime import datetime, timedelta
from pyiceberg.catalog import load_catalog

# Paste your actual bucket name from `terraform output bucket_name`
BUCKET_NAME = "riskflow-lakehouse-7d75d72b"

# 1. Load and merge — same logic as explore_data.py
transactions = pd.read_csv("data/raw/train_transaction.csv")
identity = pd.read_csv("data/raw/train_identity.csv")
merged = transactions.merge(identity, on="TransactionID", how="left")

# 2. Select a focused core set of real columns rather than all 434
core_columns = [
    "TransactionID", "TransactionDT", "TransactionAmt", "ProductCD",
    "card1", "card4", "card6", "addr1", "P_emaildomain",
    "DeviceType", "DeviceInfo", "isFraud"
]
raw_txns = merged[core_columns].copy()

# 3. Convert TransactionDT (seconds since an undocumented reference point)
# into a real timestamp, using the community-standard assumed start date.
# This is a documented assumption — see docs/cost_model_assumptions.md pattern.
reference_start = datetime(2017, 12, 1)
raw_txns["txn_timestamp"] = raw_txns["TransactionDT"].apply(
    lambda seconds: reference_start + timedelta(seconds=int(seconds))
)
raw_txns["txn_date"] = raw_txns["txn_timestamp"].dt.date.astype(str)

# 4. Rename columns to match RiskFlow's schema naming convention
raw_txns = raw_txns.rename(columns={
    "TransactionID": "txn_id",
    "TransactionAmt": "amount",
    "isFraud": "is_fraud_label",
})

# 5. Convert to Arrow — the format pyiceberg actually understands
arrow_table = pa.Table.from_pandas(raw_txns, preserve_index=False)
print("Rows to load:", arrow_table.num_rows)
print("Schema:\n", arrow_table.schema)

# 6. Connect to the catalog — identical to the test script
catalog = load_catalog(
    "riskflow",
    **{"type": "glue", "warehouse": f"s3://{BUCKET_NAME}/"}
)
print(catalog.list_tables("riskflow_lakehouse"))

# 7. Create the table if it doesn't exist yet, using Arrow's inferred schema
table_identifier = "riskflow_lakehouse.raw_transactions"

try:
    table = catalog.load_table(table_identifier)
    print("Loaded existing table:", table_identifier)
except Exception:
    table = catalog.create_table(identifier=table_identifier, schema=arrow_table.schema)
    print("Created new table:", table_identifier)

if not catalog.table_exists(table_identifier):
    table = catalog.load_table(table_identifier)
    print("Loaded existing table:", table_identifier)

# 8. Actually write the rows
table.append(arrow_table)
print("Write complete.")