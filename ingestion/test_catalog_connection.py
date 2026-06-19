from pyiceberg.catalog import load_catalog

# Paste your actual bucket name here — get it by running:
# terraform output bucket_name  (from inside the terraform/ folder)
BUCKET_NAME = "riskflow-lakehouse-7d75d72b"

catalog = load_catalog(
    "riskflow",
    **{
        "type": "glue",
        "warehouse": f"s3://{BUCKET_NAME}/",
    }
)

print("Connected successfully.")
print("Existing namespaces in Glue Catalog:", catalog.list_namespaces())