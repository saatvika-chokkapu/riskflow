import os
from dotenv import load_dotenv

load_dotenv()

print("ACCOUNT:", os.getenv("SNOWFLAKE_ACCOUNT"))
print("USER:", os.getenv("SNOWFLAKE_USER"))
print("WAREHOUSE:", os.getenv("SNOWFLAKE_WAREHOUSE"))
print("DATABASE:", os.getenv("SNOWFLAKE_DATABASE"))
print("SCHEMA:", os.getenv("SNOWFLAKE_SCHEMA"))
print("PASSWORD SET:", os.getenv("SNOWFLAKE_PASSWORD") is not None)