import json
import os
from datetime import datetime

import requests
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()


def load_city_config():
    with open("config/cities.json", "r") as f:
        return json.load(f)


def get_weather_data(city):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={city['latitude']}"
        f"&longitude={city['longitude']}"
        f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    
    response = requests.get(url, timeout=30)
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


def load_to_snowflake(city_name, weather_json):
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    insert_sql = """
    INSERT INTO WEATHER_API_DATA
    (
        INGESTION_TIMESTAMP,
        CITY,
        SOURCE,
        RAW_PAYLOAD
    )
    SELECT
        CURRENT_TIMESTAMP(),
        %s,
        'OPEN_METEO',
        PARSE_JSON(%s)
    """

    cursor.execute(
        insert_sql,
        (city_name, json.dumps(weather_json)) 
    )

    conn.commit()
    cursor.close()
    conn.close()


def main():
    cities = load_city_config()

    for city in cities:  
        print(f"Fetching weather for {city['city']}")
        
        weather_data = get_weather_data(city)  
        
        print("Loading into Snowflake...")
        
        load_to_snowflake(city['city'], weather_data)  
        
        print(f"Load completed for {city['city']}.\n")


if __name__ == "__main__":
    main()