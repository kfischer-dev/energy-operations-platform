from fastapi import FastAPI
from src.database import get_connection, fetch_stations

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Energy Operations Platform API"}

@app.get("/health")
def app_status():
    return {"status": "ok"}

@app.get("/stations")
def get_stations():
    
    conn = get_connection()
    try:
        stations = fetch_stations(conn)

    finally:
        conn.close()
    
    return stations