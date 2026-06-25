def print_measurements(rows):

    print("\nMeasurements by station:")
    print("-" * 70)

    for row in rows:
        station_name, time, load_value, unit = row
        print(f"{station_name:10} | {time:%Y-%m-%d %H:%M} | {load_value:>8} {unit}")

    print("-" * 70)
    print(f"Total rows: {len(rows)}")

def print_stations(rows):

    print("\nStations:\n")

    for row in rows:
        station_id, station_name, station_type, station_location = row
        print(f"{station_id} | {station_name:10} | {station_type:16} | {station_location}")

    print()
    print(f"Total stations: {len(rows)}")