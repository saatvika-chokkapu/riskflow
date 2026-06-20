import os
from dotenv import load_dotenv
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from pyiceberg.catalog import load_catalog

load_dotenv()

BUCKET_NAME = "riskflow-lakehouse-7d75d72b"

# Pull from the lakehouse — same source as everything else in this project
catalog = load_catalog("riskflow", **{"type": "glue", "warehouse": f"s3://{BUCKET_NAME}/"})
table = catalog.load_table("riskflow_lakehouse.raw_transactions")
df = table.scan().to_pandas()

print("Loaded from lakehouse:", df.shape)

# Snowflake convention is uppercase column names by default
df.columns = [col.upper() for col in df.columns]

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
    df,
    table_name="RAW_TRANSACTIONS",
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA"),
    auto_create_table=True,
    overwrite=True,
)

print(f"Success: {success} | Rows loaded: {num_rows} | Chunks: {num_chunks}")

conn.close()