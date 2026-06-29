import logging
from src.logging_config import configure_logging

from fastapi import FastAPI
from src.database import get_connection, fetch_stations, fetch_joined_measurements

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
def home():
    logger.info("=" * 60)
    logger.info("Root endpoint called")
    logger.info("=" * 60)
    return {"message": "Energy Operations Platform API"}

@app.get("/health")
def app_status():
    logger.info("=" * 60)
    logger.info("Health endpoint called")
    logger.info("=" * 60)   
    return {"status": "ok"}

@app.get("/stations")
def get_stations():
    logger.info("=" * 60)
    logger.info("GET /stations request received. Opening database connection.")

    conn = get_connection()

    logger.info("Loading station data from database.")

    try:
        station_data = fetch_stations(conn)
        logger.info(f"Loaded {len(station_data)} stations from database.")

    finally:
        conn.close()
        logger.info("Database connection closed.")
        logger.info("=" * 60)
    return station_data

@app.get("/measurements")
def get_measurements():
    logger.info("=" * 60)
    logger.info("GET /measurements request received. Opening database connection.")

    conn = get_connection()

    logger.info("Loading joined measurement data from database.")

    try:
        measurement_data = fetch_joined_measurements(conn)
        logger.info(f"Loaded {len(measurement_data)} joined measurements from database.")

    finally:
        conn.close()
        logger.info("Database connection closed.")
        logger.info("=" * 60)
    return measurement_data