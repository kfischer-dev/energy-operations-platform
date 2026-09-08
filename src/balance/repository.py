def fetch_balance_measurements(
    conn,
    start_time,
    end_time,
) -> list[dict]:
    """Fetch measurements required for energy balance calculation.

    Only producer and consumer assets with at least one valid measurement
    inside the requested period are considered.

    For those assets, the latest valid measurement before start_time and
    the earliest valid measurement after end_time are included as boundary
    support points.
    """

    with conn.cursor() as cursor:
        cursor.execute(
            """
            WITH relevant_assets AS (
                SELECT DISTINCT m.asset_id
                FROM measurements AS m
                JOIN assets AS a
                    ON a.asset_id = m.asset_id
                JOIN asset_types AS at
                    ON at.asset_type_id = a.asset_type_id
                WHERE
                    at.asset_role IN ('producer', 'consumer')
                    AND m.quality_status = 'valid'
                    AND m.measurement_time >= %s
                    AND m.measurement_time <= %s
            ),

            left_support AS (
                SELECT DISTINCT ON (m.asset_id)
                    m.asset_id,
                    m.measurement_time,
                    m.active_power_kw,
                    m.source,
                    m.quality_status
                FROM measurements AS m
                WHERE
                    m.asset_id IN (
                        SELECT asset_id
                        FROM relevant_assets
                    )
                    AND m.quality_status = 'valid'
                    AND m.measurement_time < %s
                ORDER BY
                    m.asset_id,
                    m.measurement_time DESC
            ),

            period_measurements AS (
                SELECT
                    m.asset_id,
                    m.measurement_time,
                    m.active_power_kw,
                    m.source,
                    m.quality_status
                FROM measurements AS m
                WHERE
                    m.asset_id IN (
                        SELECT asset_id
                        FROM relevant_assets
                    )
                    AND m.quality_status = 'valid'
                    AND m.measurement_time >= %s
                    AND m.measurement_time <= %s
            ),

            right_support AS (
                SELECT DISTINCT ON (m.asset_id)
                    m.asset_id,
                    m.measurement_time,
                    m.active_power_kw,
                    m.source,
                    m.quality_status
                FROM measurements AS m
                WHERE
                    m.asset_id IN (
                        SELECT asset_id
                        FROM relevant_assets
                    )
                    AND m.quality_status = 'valid'
                    AND m.measurement_time > %s
                ORDER BY
                    m.asset_id,
                    m.measurement_time ASC
            )

            SELECT *
            FROM (
                SELECT * FROM left_support

                UNION ALL

                SELECT * FROM period_measurements

                UNION ALL

                SELECT * FROM right_support
            ) AS balance_measurements

            ORDER BY
                asset_id,
                measurement_time;
            """,
            (
                start_time,
                end_time,
                start_time,
                start_time,
                end_time,
                end_time,
            ),
        )

        rows = cursor.fetchall()

    return [
        {
            "asset_id": row[0],
            "measurement_time": row[1],
            "active_power_kw": float(row[2]),
            "source": row[3],
            "quality_status": row[4],
        }
        for row in rows
    ]
