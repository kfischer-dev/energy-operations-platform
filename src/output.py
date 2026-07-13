def print_measurements(measurement_data):
    """Print measurement dictionaries returned by the database layer."""

    print("\nMeasurements by asset:")
    print("-" * 70)

    for measurement in measurement_data:
        print(f"{measurement['asset_name']:10} | {measurement['measurement_time']:%Y-%m-%d %H:%M} | {measurement['load_value']:>8} {measurement['unit']}")

    print("-" * 70)
    print(f"Total Measurements: {len(measurement_data)}")

def print_assets(asset_data):
    """Print asset dictionaries in a readable terminal format."""

    print("\nAssets:\n")

    for asset in asset_data:
        print(f"{asset['asset_id']} | {asset['asset_name']:10} | {asset['asset_type']:16} | {asset['asset_location']}")

    print()
    print(f"Total Assets: {len(asset_data)}")

def print_database_report(asset_data, measurement_data):

    print_assets(asset_data) 
    print_measurements(measurement_data) 