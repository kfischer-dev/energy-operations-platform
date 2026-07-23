from collections import Counter

from src.database import get_connection
from src.simulation.default_data import create_default_simulation_config
from src.simulation.service import (
    load_simulation_assets,
    simulate_database_assets,
)


def run_simulation_service_smoke_test() -> bool:
    """Verify that only database assets are included in the simulation output."""

    config = create_default_simulation_config()
    conn = get_connection()

    try:
        database_assets = load_simulation_assets(conn)
        intervals = simulate_database_assets(conn, config)
    finally:
        conn.close()

    database_asset_ids = {asset.asset_id for asset in database_assets}
    interval_count_by_asset = Counter(interval.asset_id for interval in intervals)
    simulated_asset_ids = set(interval_count_by_asset)

    missing_asset_ids = database_asset_ids - simulated_asset_ids
    unexpected_asset_ids = simulated_asset_ids - database_asset_ids
    expected_intervals_per_asset = config.total_intervals
    assets_with_wrong_interval_count = {
        asset_id: interval_count
        for asset_id, interval_count in interval_count_by_asset.items()
        if interval_count != expected_intervals_per_asset
    }

    passed = bool(database_assets) and not (
        missing_asset_ids
        or unexpected_asset_ids
        or assets_with_wrong_interval_count
    )

    print("=" * 60)
    print("SIMULATION SERVICE SMOKE TEST")
    print("=" * 60)
    print(f"Datenbank-Assets:          {len(database_assets)}")
    print(f"Simulierte Assets:         {len(simulated_asset_ids)}")
    print(f"Erzeugte Intervalle:       {len(intervals)}")
    print(f"Intervalle je Asset:       {expected_intervals_per_asset}")
    print("-" * 60)

    if database_assets:
        print("Asset-ID | Asset-Code       | Asset-Typ            | Intervalle")
        print("-" * 60)
        for asset in database_assets:
            interval_count = interval_count_by_asset.get(asset.asset_id, 0)
            print(
                f"{asset.asset_id:>8} | "
                f"{asset.asset_code:<16} | "
                f"{asset.asset_type:<20} | "
                f"{interval_count:>10}"
            )
    else:
        print("Keine unterstuetzten Simulations-Assets in der Datenbank gefunden.")

    print("-" * 60)

    if missing_asset_ids:
        print(f"Fehlende Asset-IDs:         {sorted(missing_asset_ids)}")
    if unexpected_asset_ids:
        print(f"Unerwartete Asset-IDs:      {sorted(unexpected_asset_ids)}")
    if assets_with_wrong_interval_count:
        print(
            "Falsche Intervallanzahl:    "
            f"{assets_with_wrong_interval_count}"
        )

    print(f"Ergebnis:                   {'BESTANDEN' if passed else 'FEHLGESCHLAGEN'}")
    print("=" * 60)

    return passed


if __name__ == "__main__":
    raise SystemExit(0 if run_simulation_service_smoke_test() else 1)
