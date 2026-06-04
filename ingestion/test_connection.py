import os
from dotenv import load_dotenv
import snowflake.connector

load_dotenv()

print("Connecting to Snowflake...")

conn = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA"),
    role=os.getenv("SNOWFLAKE_ROLE")
)

cursor = conn.cursor()

cursor.execute("""
SELECT
    CURRENT_USER(),
    CURRENT_ROLE(),
    CURRENT_DATABASE(),
    CURRENT_SCHEMA(),
    CURRENT_WAREHOUSE()
""")

result = cursor.fetchone()

print("\nConnection Successful!")
print(f"User: {result[0]}")
print(f"Role: {result[1]}")
print(f"Database: {result[2]}")
print(f"Schema: {result[3]}")
print(f"Warehouse: {result[4]}")

cursor.close()
conn.close()

print("\nConnection Closed.")