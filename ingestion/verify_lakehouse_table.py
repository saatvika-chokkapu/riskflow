from pyiceberg.catalog import load_catalog

BUCKET_NAME = "riskflow-lakehouse-7d75d72b"

catalog = load_catalog(
    "riskflow",
    **{"type": "glue", "warehouse": f"s3://{BUCKET_NAME}/"}
)

table = catalog.load_table("riskflow_lakehouse.raw_transactions")

# Read the table back into a pandas DataFrame
df = table.scan().to_pandas()

print("Row count:", len(df))
print("\nFraud label distribution:")
print(df["is_fraud_label"].value_counts())
print("\nDate range:")
print(df["txn_date"].min(), "to", df["txn_date"].max())
print("\nFirst few rows:")
print(df.head())