def print_measurements(rows):

    print("\nMeasurements by station:")
    print("-" * 70)

    for row in rows:
        station_name, time, load_value, unit = row
        print(f"{station_name:10} | {time:%Y-%m-%d %H:%M} | {load_value:>8} {unit}")

    print("-" * 70)
    print(f"Total rows: {len(rows)}")