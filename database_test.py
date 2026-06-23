import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")

print("Connecting to PostgreSQL database...")

conn = psycopg.connect(dbname = db_name, user = db_user, password = db_password, host = db_host, port = db_port)

print("Database connection successful")

cursor = conn.cursor()

cursor.execute("""
    SELECT
        stations.station_name,
        measurements.measurement_time,
        measurements.load_value,
        measurements.unit
    FROM measurements
    JOIN stations
        ON measurements.station_id = stations.station_id
    ORDER BY stations.station_name, measurements.measurement_time;
""")

rows = cursor.fetchall()

print("\nMesurements by station:")
print("-" * 70)

for row in rows:
    station_name, time, load_value, unit = row
    print(f"{station_name:10} | {time:%Y-%m-%d %H:%M} | {load_value:>8} {unit}")

print("-" * 70)
print(f"Total rows: {len(rows)}")

conn.close()

print("\nConnection closed.")