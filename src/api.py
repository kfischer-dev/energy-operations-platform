import logging
from src.logging_config import configure_logging

from fastapi import FastAPI, HTTPException, status, Query, Path
from src.database import get_connection, fetch_stations, fetch_joined_measurements, fetch_measurements_by_station_id, fetch_station_by_id
from src.schemas import StationResponse, MeasurementResponse

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Energy Operations Platform API",
    description=(
        "REST API for accessing energy station and measurement data. "
        "This API is part of the Energy Operations Platform portfolio project."
    ),
    version="0.5.1",
    openapi_tags=[
        {
            "name": "General",
            "description": "General API information and health checks.",
        },
        {
            "name": "Stations",
            "description": "Endpoints for accessing energy station master data.",
        },
        {
            "name": "Measurements",
            "description": "Endpoints for accessing station measurement data.",
        },
    ],
)

# ============================================================
# General Endpoints
# ============================================================

@app.get("/", 
    tags=["General"],
    summary="API root",
    description=(
        "Returns a simple welcome message for the Energy Operations Platform API. "
        "This endpoint can be used to verify that the API is reachable."
    ),
    response_description="Welcome message for the API.",
)
def home():
    logger.info("=" * 60)
    logger.info("Root endpoint called")
    logger.info("=" * 60)
    return {"message": "Energy Operations Platform API"}

@app.get("/health", 
    tags=["General"],
    summary="Health check",
    description=(
        "Returns the current health status of the API. "
        "This endpoint is intended as a lightweight check to confirm that the service is running."
    ),
    response_description="Current API health status.",
)
def app_status():
    logger.info("=" * 60)
    logger.info("Health endpoint called")
    logger.info("=" * 60)   
    return {"status": "ok"}

# ============================================================
# Station Endpoints
# ============================================================

@app.get("/stations",
    response_model=list[StationResponse],
    tags=["Stations"],
    summary="Get all stations",
    description=(
        "Returns all energy stations stored in the PostgreSQL database. "
        "Each station contains master data such as ID, name, location and station type. "
        "Station types can represent different energy assets, for example solar_park, "
        "wind_park, hydro_plant, battery_storage or substation."   
    ),
    response_description="List of station records.",
)
def get_stations(station_type: str | None = Query(default=None, description="Optional filter by station type, for example solar_park or wind_park.")):
    """Return all stations, optionally filtered by station type."""

    logger.info("=" * 60)
    logger.info("GET /stations request received. Opening database connection.")

    conn = get_connection()

    logger.info("Loading station data from database.")

    try:
        station_data = fetch_stations(conn)
        logger.info(f"Loaded {len(station_data)} stations from database.")

        if station_type is not None:
            logger.info(f"Applying station_type filter: {station_type}")
            station_by_type = []
            for station in station_data:
                if station_type == station["station_type"]:
                    station_by_type.append(station)
            logger.info(f"Returned {len(station_by_type)} stations")
            return station_by_type

        return station_data

    finally:
        conn.close()
        logger.info("Database connection closed.")
        logger.info("=" * 60)


@app.get("/stations/{station_id}", 
    response_model=StationResponse,
    tags=["Stations"],
    summary="Get station by ID",
    description=(
        "Returns one energy station by its station ID. "
        "If no station exists for the given ID, the API returns a 404 error."
    ),
    response_description="Single station record.",
)
def get_station_by_id(station_id: int = Path(..., ge=1, description="Unique ID of the requested energy station.")):
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

# ============================================================
# Measurement Endpoints
# ============================================================

@app.get("/measurements", 
    response_model=list[MeasurementResponse],
    tags=["Measurements"],
    summary="Get measurements",
    description=(
        "Returns joined measurement data from the PostgreSQL database. "
        "The response includes measurement values together with related station information. "
        "An optional limit query parameter can be used to restrict the number of returned records."
    ),
    response_description="List of measurement records, optionally limited by the query parameter.",
)
def get_measurements(limit: int | None = Query(default=None, ge=1, le=100, description="optional maximum number of returned measurements, 1 to 100")):
    """Return measurements filtered by limit."""

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

@app.get("/stations/{station_id}/measurements", 
    response_model=list[MeasurementResponse],
    tags=["Stations", "Measurements"],
    summary="Get measurements by station ID",
    description=(
        "Returns all measurement records for one specific energy station. "
        "The endpoint first checks whether the requested station exists. "
        "If no station exists for the given station ID, the API returns a 404 error."
    ),
    response_description="List of measurement records for the requested station.",   
)
def get_measurements_by_station_id(station_id: int = Path(..., ge=1, description="Unique ID of the requested energy station.")):
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

    
