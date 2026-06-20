import pandas as pd
import joblib
from pyiceberg.catalog import load_catalog

BUCKET_NAME = "riskflow-lakehouse-7d75d72b"

catalog = load_catalog("riskflow", **{"type": "glue", "warehouse": f"s3://{BUCKET_NAME}/"})
table = catalog.load_table("riskflow_lakehouse.raw_transactions")
df = table.scan().to_pandas()

categorical_cols = ["ProductCD", "card4", "card6", "P_emaildomain", "DeviceType", "DeviceInfo"]

encoders = {}
for col in categorical_cols:
    categories = df[col].astype("category").cat.categories
    # Build the exact same value -> code mapping pandas used during training
    encoders[col] = {category: code for code, category in enumerate(categories)}

joblib.dump(encoders, "backend/encoders.pkl")
print("Saved category encoders for columns:", list(encoders.keys()))
for col, mapping in encoders.items():
    print(f"  {col}: {len(mapping)} categories")