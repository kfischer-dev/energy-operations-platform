import logging
from src.logging_config import configure_logging

from fastapi import FastAPI, HTTPException, status, Query
from src.database import get_connection, fetch_stations, fetch_joined_measurements, fetch_measurements_by_station_id, fetch_station_by_id

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
    """Return all stations."""

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

@app.get("/stations/{station_id}")
def get_station_by_id(station_id: int):
    """Return one station by ID."""

    logger.info("=" * 60)
    logger.info(f"GET /stations/{station_id} request received. Opening database connection.")

    conn = get_connection()

    logger.info("Loading station data from database.")

    try:
        station = fetch_station_by_id(conn, station_id)

        if station is None:
            logger.warning(f"Station with id {station_id} not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Station with id {station_id} not found")

        return station

    finally:
        conn.close()
        logger.info("Database connection closed.")
        logger.info("=" * 60)

@app.get("/measurements")
def get_measurements(limit: int | None = Query(default=None, ge=1, le=100)):
    logger.info("=" * 60)
    logger.info("GET /measurements request received. Opening database connection.")

    conn = get_connection()

    logger.info("Loading joined measurement data from database.")

    try:
        measurement_data = fetch_joined_measurements(conn)
        logger.info(f"Loaded {len(measurement_data)} joined measurements from database.")

        if limit is not None:
            logger.info(f"Applying limit={limit} to measurement response.")
            return measurement_data[:limit]
        
        return measurement_data

    finally:
        conn.close()
        logger.info("Database connection closed.")
        logger.info("=" * 60)

@app.get("/stations/{station_id}/measurements")
def get_measurements_by_station_id(station_id: int):
    """Return all measurements for one station."""

    logger.info("=" * 60)
    logger.info(f"GET /stations/{station_id}/measurements request received. Opening database connection.")

    conn = get_connection()

    try:
        # Check the parent station first so a missing station returns 404 instead of [].
        logger.info("Loading station data from database.")
        station = fetch_station_by_id(conn, station_id)
        if station is None:
            logger.warning(f"Station with id {station_id} not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Station with id {station_id} not found")
        
        logger.info("Loading joined measurement data from database.")
        measurement_data = fetch_measurements_by_station_id(conn, station_id)
        logger.info(f"Loaded {len(measurement_data)} joined measurements of station_id {station_id} from database.")

    finally:
        conn.close()
        logger.info("Database connection closed.")
        logger.info("=" * 60)

    return measurement_data

    
