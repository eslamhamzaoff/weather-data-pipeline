import json
import os
from datetime import datetime

import requests
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

def get_weather_data():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=30.0444"
        "&longitude=31.2357"
        "&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    
    response = requests.get(url , timeout=30)
    response.raise_for_status()
    return response.json()


def get_snowflake_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role=os.getenv("SNOWFLAKE_ROLE")
    )



def load_to_snowflake(weather_json):
    conn = get_snowflake_connection()
    
    cursor = conn.cursor()

    insert_sql = """
    INSERT INTO WEATHER_API_DATA
    (
    INGESTION_TIMESTAMP,
    SOURCE,
    RAW_PAYLOAD
    )
    SELECT
    CURRENT_TIMESTAMP(),
    'OPEN_METEO',
    PARSE_JSON(%s)
    """

    cursor.execute(
        insert_sql,
        (json.dumps(weather_json),)
    )

    conn.commit()

    cursor.close()
    conn.close()

def main():
    print("Fetching weather data...")

    weather_data = get_weather_data()

    print("Loading into Snowflake...")

    load_to_snowflake(weather_data)

    print("Load completed successfully.")


if __name__ == "__main__":
    main()

