def print_measurements(measurement_data):
    """Print measurement dictionaries returned by the database layer."""

    print("\nMeasurements by station:")
    print("-" * 70)

    for measurement in measurement_data:
        print(f"{measurement['station_name']:10} | {measurement['measurement_time']:%Y-%m-%d %H:%M} | {measurement['load_value']:>8} {measurement['unit']}")

    print("-" * 70)
    print(f"Total Measurements: {len(measurement_data)}")

def print_stations(station_data):
    """Print station dictionaries in a readable terminal format."""

    print("\nStations:\n")

    for station in station_data:
        print(f"{station['station_id']} | {station['station_name']:10} | {station['station_type']:16} | {station['station_location']}")

    print()
    print(f"Total Stations: {len(station_data)}")

def print_database_report(station_data, measurement_data):

    print_stations(station_data) 
    print_measurements(measurement_data) 