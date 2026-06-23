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
    SELECT station_id, station_name, station_type, station_location
    FROM stations
    ORDER BY station_id;
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()

print("Connection closed.")