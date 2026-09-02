import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException, Path, Query, status

from src.database import (
    create_measurement,
    fetch_asset_by_id,
    fetch_asset_summaries,
    fetch_measurement_by_id,
    fetch_measurement_kpi_summary,
    fetch_measurement_summaries,
    fetch_measurement_summaries_by_asset_id,
    fetch_measurements_for_asset_kpi_period,
    get_connection,
    update_measurement_quality_status,
)
from src.logging_config import configure_logging
from src.measurements.service import (
    calculate_asset_kpis,
    calculate_kpis_for_all_measurements,
)
from src.schemas import (
    AssetKPIsResponse,
    AssetResponse,
    AssetSummaryResponse,
    MeasurementCreate,
    MeasurementKPIsResponse,
    MeasurementQualityUpdate,
    MeasurementResponse,
    MeasurementSummaryResponse,
)

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Energy Operations Platform API",
    description=(
        "REST API for accessing energy asset and measurement data. "
        "This API is part of the Energy Operations Platform portfolio project."
    ),
    version="0.12.0",
    openapi_tags=[
        {
            "name": "General",
            "description": "General API information and health checks.",
        },
        {
            "name": "Assets",
            "description": "Endpoints for accessing energy asset master data.",
        },
        {
            "name": "Measurements",
            "description": "Endpoints for accessing asset measurement data.",
        },
        {
            "name": "KPIs",
            "description": "Endpoints for accessing KPI data.",
        },
    ],
)

# ============================================================
# API helper functions
# ============================================================


def get_asset_or_404(conn, asset_id):
    asset = fetch_asset_by_id(conn, asset_id)

    if asset is None:
        logger.warning(f"Asset with id {asset_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with id {asset_id} not found",
        )

    return asset


def get_measurement_or_404(conn, measurement_id):
    measurement = fetch_measurement_by_id(conn, measurement_id)

    if measurement is None:
        logger.warning(f"Measurement with id {measurement_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Measurement with id {measurement_id} not found",
        )

    return measurement


# ============================================================
# General Endpoints
# ============================================================


@app.get(
    "/",
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


@app.get(
    "/health",
    tags=["General"],
    summary="Health check",
    description=(
        "Returns the current health status of the API. "
        "This endpoint is intended as a lightweight check to confirm that "
        "the service is running."
    ),
    response_description="Current API health status.",
)
def app_status():
    logger.info("=" * 60)
    logger.info("Health endpoint called")
    logger.info("=" * 60)
    return {"status": "ok"}


# ============================================================
# Asset Endpoints
# ============================================================


@app.get(
    "/assets",
    response_model=list[AssetSummaryResponse],
    tags=["Assets"],
    summary="Get all assets",
    description=(
        "Returns all energy assets stored in the PostgreSQL database. "
        "Each asset contains master data such as ID, name, location and asset type. "
        "Asset types can represent different energy assets, for example solar_park, "
        "wind_park, hydro_power_plant, battery_storage or substation."
    ),
    response_description="List of asset records.",
)
def get_assets(
    asset_type: str | None = Query(
        default=None,
        description=(
            "Optional filter by asset type, for example solar_park or wind_park."
        ),
    ),
):
    """Return all assets, optionally filtered by asset type."""

    logger.info("=" * 60)
    logger.info("GET /assets request received. Opening database connection.")

    conn = get_connection()

    logger.info("Loading asset data from database.")

    try:
        asset_data = fetch_asset_summaries(conn)
        logger.info(f"Loaded {len(asset_data)} assets from database.")

        if asset_type is not None:
            logger.info(f"Applying asset_type filter: {asset_type}")
            asset_by_type = [
                asset for asset in asset_data if asset_type == asset["asset_type"]
            ]
            logger.info(f"Returned {len(asset_by_type)} assets")
            return asset_by_type

        return asset_data

    finally:
        conn.close()
        logger.info("Database connection closed.")
        logger.info("=" * 60)


@app.get(
    "/assets/{asset_id}",
    response_model=AssetResponse,
    tags=["Assets"],
    summary="Get asset by ID",
    description=(
        "Returns one energy asset by its asset ID. "
        "If no asset exists for the given ID, the API returns a 404 error."
    ),
    response_description="Single asset record.",
)
def get_asset_by_id(
    asset_id: int = Path(
        ...,
        ge=1,
        description="Unique ID of the requested energy asset.",
    ),
):
    """Return one asset by ID."""

    logger.info("=" * 60)
    logger.info(
        f"GET /assets/{asset_id} request received. Opening database connection."
    )

    conn = get_connection()

    logger.info("Loading asset data from database.")

    try:
        asset = get_asset_or_404(conn, asset_id)
        return asset

    finally:
        conn.close()
        logger.info("Database connection closed.")
        logger.info("=" * 60)


# ============================================================
# Measurement Endpoints
# ============================================================


@app.get(
    "/measurements",
    response_model=list[MeasurementSummaryResponse],
    tags=["Measurements"],
    summary="Get measurements",
    description=(
        "Returns joined measurement data from the PostgreSQL database. "
        "The response includes measurement values together with related asset "
        "information. "
        "An optional limit query parameter can be used to restrict the number "
        "of returned records."
    ),
    response_description=(
        "List of measurement records, optionally limited by the query parameter."
    ),
)
def get_measurements(
    limit: int | None = Query(
        default=None,
        ge=1,
        le=100,
        description="Optional maximum number of returned measurements, 1 to 100.",
    ),
):
    """Return measurements filtered by limit."""

    logger.info("=" * 60)
    logger.info("GET /measurements request received. Opening database connection.")

    conn = get_connection()

    logger.info("Loading joined measurement data from database.")

    try:
        measurement_data = fetch_measurement_summaries(conn)
        logger.info(
            f"Loaded {len(measurement_data)} joined measurements from database."
        )

        if limit is not None:
            logger.info(f"Applying limit={limit} to measurement response.")
            return measurement_data[:limit]

        return measurement_data

    finally:
        conn.close()
        logger.info("Database connection closed.")
        logger.info("=" * 60)


@app.get(
    "/assets/{asset_id}/measurements",
    response_model=list[MeasurementSummaryResponse],
    tags=["Assets", "Measurements"],
    summary="Get measurements by asset ID",
    description=(
        "Returns all measurement records for one specific energy asset. "
        "The endpoint first checks whether the requested asset exists. "
        "If no asset exists for the given asset ID, the API returns a 404 error."
    ),
    response_description="List of measurement records for the requested asset.",
)
def get_measurements_by_asset_id(
    asset_id: int = Path(
        ...,
        ge=1,
        description="Unique ID of the requested energy asset.",
    ),
    limit: int | None = Query(
        default=None,
        ge=1,
        le=100,
        description=(
            "Optional maximum number of measurement records to return for this asset."
        ),
    ),
):
    """Return all measurements for one asset."""

    logger.info("=" * 60)
    logger.info(
        f"GET /assets/{asset_id}/measurements request received. "
        "Opening database connection."
    )

    conn = get_connection()

    try:
        # Check the parent asset first so a missing asset returns 404 instead of [].
        logger.info("Loading asset data from database.")
        get_asset_or_404(conn, asset_id)

        logger.info("Loading joined measurement data from database.")
        measurement_data = fetch_measurement_summaries_by_asset_id(conn, asset_id)
        logger.info(
            f"Loaded {len(measurement_data)} joined measurements of "
            f"asset_id {asset_id} from database."
        )

        if limit is not None:
            logger.info(f"Applying limit={limit} to asset measurement response.")
            return measurement_data[:limit]

        return measurement_data

    finally:
        conn.close()
        logger.info("Database connection closed.")
        logger.info("=" * 60)


@app.get(
    "/measurements/{measurement_id}",
    response_model=MeasurementResponse,
    tags=["Measurements"],
    summary="Get measurement by ID",
    description=(
        "Returns one specific point-in-time power measurement by its measurement ID. "
        "The response includes the asset ID, measurement timestamp, active power, "
        "source and quality status. "
        "If no measurement exists for the given ID, the API returns a 404 error."
    ),
    response_description="Single measurement record.",
)
def get_measurement_by_id(
    measurement_id: int = Path(
        ...,
        ge=1,
        description="Unique ID of the requested measurement record.",
    ),
):
    logger.info("=" * 60)
    logger.info(
        f"GET /measurements/{measurement_id} request received. "
        "Opening database connection."
    )

    conn = get_connection()

    logger.info("Loading measurement data from database.")

    try:
        measurement = get_measurement_or_404(conn, measurement_id)
        return measurement

    finally:
        conn.close()
        logger.info("Database connection closed.")
        logger.info("=" * 60)


# ============================================================
# POST Measurement Endpoints
# ============================================================


@app.post(
    "/measurements",
    response_model=MeasurementResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Measurements"],
    summary="Create a new asset measurement",
    description=(
        "Creates a new point-in-time power measurement and assigns it to an existing "
        "energy asset. The endpoint accepts the asset ID, measurement timestamp, "
        "active power, source and quality status. "
        "After validation, the measurement is stored in the PostgreSQL database "
        "and can be retrieved through the measurement endpoints."
    ),
    response_description="The newly created measurement record.",
)
def post_measurement(measurement_data: MeasurementCreate):
    """Post measurement for specific asset."""

    logger.info("=" * 60)
    logger.info(
        f"POST /measurements request received for asset_id {measurement_data.asset_id}."
    )

    conn = get_connection()

    try:
        get_asset_or_404(conn, measurement_data.asset_id)

        measurement_id = create_measurement(conn, measurement_data)
        logger.info(
            f"Measurement for asset_id {measurement_data.asset_id} successfully "
            f"saved to measurement_id {measurement_id}."
        )
        measurement = fetch_measurement_by_id(conn, measurement_id)

        return measurement

    finally:
        conn.close()
        logger.info("Database connection closed.")
        logger.info("=" * 60)


@app.patch(
    "/measurements/{measurement_id}",
    response_model=MeasurementResponse,
    status_code=status.HTTP_200_OK,
    tags=["Measurements"],
    summary="Update measurement quality status",
    description=(
        "Updates the quality status of an existing measurement record. "
        "Allowed values are valid, invalid and estimated. "
        "The endpoint returns the updated measurement record."
    ),
    response_description="Updated measurement record.",
)
def patch_quality_status_by_measurement_id(
    measurement_id: int = Path(
        ...,
        ge=1,
        description="Unique ID of the requested measurement record.",
    ),
    update_data: MeasurementQualityUpdate = ...,
):
    """Patch quality_status for specific measurement."""

    logger.info("=" * 60)
    logger.info(
        f"PATCH /measurements/{measurement_id} request received for "
        f"measurement_id {measurement_id}."
    )

    conn = get_connection()

    try:
        get_measurement_or_404(conn, measurement_id)

        measurement_id = update_measurement_quality_status(
            conn,
            measurement_id,
            update_data.quality_status,
        )
        logger.info(
            f"Measurement quality_status for measurement_id {measurement_id} "
            f"successfully updated to {update_data.quality_status}."
        )
        new_measurement = fetch_measurement_by_id(conn, measurement_id)

        return new_measurement

    finally:
        conn.close()
        logger.info("Database connection closed.")
        logger.info("=" * 60)


# ============================================================
# GET kpi Endpoints
# ============================================================


@app.get(
    "/kpis/measurements",
    response_model=MeasurementKPIsResponse,
    status_code=status.HTTP_200_OK,
    tags=["KPIs"],
    summary="Get global measurement KPI summary",
    description=(
        "Returns global KPI values across all energy assets for a requested time period. "
        "Minimum and maximum power are based on actual valid measurements within "
        "the requested period. Average power and total energy are derived separately "
        "for each asset from its time-dependent power curve and then aggregated. "
        "Measurements outside the requested period may be used as support points "
        "for boundary interpolation. Coverage indicates the average temporal data "
        "coverage across the evaluated assets."
    ),
)
def get_measurement_kpi_summary(
    start_time: datetime = Query(
        ...,
        description="Start time for the KPI summary period.",
    ),
    end_time: datetime = Query(
        ...,
        description="End time for the KPI summary period.",
    ),
):
    """Get measurement KPI summary."""

    logger.info("=" * 60)
    logger.info("GET /kpis/measurements request received.")

    if end_time <= start_time:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="end_time must be after start_time",
        )

    conn = get_connection()

    try:
        measurements = fetch_measurement_kpi_summary(conn, start_time, end_time)

        kpi_summary = calculate_kpis_for_all_measurements(
            measurements=measurements,
            start_time=start_time,
            end_time=end_time,
        )

        logger.info(
            f"Calculated global KPI summary from "
            f"{kpi_summary['measurement_count']} measurements within the requested period."
        )

        return kpi_summary

    finally:
        conn.close()
        logger.info("Database connection closed.")
        logger.info("=" * 60)


@app.get(
    "/assets/{asset_id}/kpis",
    response_model=AssetKPIsResponse,
    status_code=status.HTTP_200_OK,
    tags=["KPIs"],
    summary="Get KPI summary for an asset",
    description=(
        "Returns KPI values for one energy asset over a requested time period. "
        "Minimum and maximum power are based on actual valid measurements within "
        "the requested period. Average power and total energy are derived from the "
        "time-dependent power curve using interpolation at period boundaries when "
        "required. Measurements outside the requested period may be used only as "
        "support points for boundary interpolation."
    ),
)
def get_asset_kpi_summary(
    asset_id: int = Path(
        ...,
        ge=1,
        description="Unique ID of the requested energy asset.",
    ),
    start_time: datetime = Query(
        ...,
        description="Start time for the KPI summary period.",
    ),
    end_time: datetime = Query(
        ...,
        description="End time for the KPI summary period.",
    ),
):
    """Get KPI summary for one specific asset at a given time period."""

    logger.info("=" * 60)
    logger.info(f"GET /assets/{asset_id}/kpis request received.")

    if end_time <= start_time:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="end_time must be after start_time",
        )

    conn = get_connection()

    try:
        asset = get_asset_or_404(conn, asset_id)

        measurements = fetch_measurements_for_asset_kpi_period(
            conn,
            asset_id=asset_id,
            start_time=start_time,
            end_time=end_time,
        )

        kpi_summary = calculate_asset_kpis(
            measurements=measurements,
            asset_id=asset_id,
            start_time=start_time,
            end_time=end_time,
        )

        logger.info(
            f"Loaded KPI summary for {asset['asset_name']} with "
            f"{kpi_summary['measurement_count']} valid measurements."
        )

        return {
            "asset_id": asset["asset_id"],
            "asset_name": asset["asset_name"],
            **kpi_summary,
        }

    finally:
        conn.close()
        logger.info("Database connection closed.")
        logger.info("=" * 60)
