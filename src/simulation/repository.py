import logging

logger = logging.getLogger(__name__)


def fetch_simulation_assets(conn, supported_asset_types: list[str]) -> list[dict]:
    """Return all database assets required by the simulation."""

    with conn.cursor() as cursor:
        logger.debug("Executing simulation asset query.")

        cursor.execute(
            """
            SELECT
                a.asset_id,
                a.asset_code,
                at.asset_role,
                at.asset_type_name,
                r.region_id,
                r.region_code,
                a.rated_power_kw,
                a.operating_status,
                at.is_renewable,
                at.is_weather_dependent,
                at.is_dispatchable,
                at.can_store_energy
            FROM assets AS a
            JOIN asset_types AS at
                ON at.asset_type_id = a.asset_type_id
            JOIN regions AS r
                ON r.region_id = a.region_id
            WHERE at.asset_type_name = ANY(%s)
            ORDER BY a.asset_id;
        """,
            (supported_asset_types,),
        )

        rows = cursor.fetchall()

    return [map_simulation_asset_row(row) for row in rows]


# ============================================================
# Mapper
# ============================================================


def map_simulation_asset_row(row):
    (
        asset_id,
        asset_code,
        asset_role,
        asset_type,
        region_id,
        region_code,
        rated_power_kw,
        operating_status,
        is_renewable,
        is_weather_dependent,
        is_dispatchable,
        can_store_energy,
    ) = row

    return {
        "asset_id": asset_id,
        "asset_code": asset_code,
        "asset_role": asset_role,
        "asset_type": asset_type,
        "region_id": region_id,
        "region_code": region_code,
        "rated_power_kw": rated_power_kw,
        "operating_status": operating_status,
        "is_renewable": is_renewable,
        "is_weather_dependent": is_weather_dependent,
        "is_dispatchable": is_dispatchable,
        "can_store_energy": can_store_energy,
    }
