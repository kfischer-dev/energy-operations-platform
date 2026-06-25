# =============================================================
# Energy Operations Platform
#
# Current development focus: v0.4
#
# This script currently starts the PostgreSQL-based application flow:
# 1. Open a PostgreSQL database connection.
# 2. Load joined station and measurement data from the database.
# 3. Print the retrieved measurement data to the terminal.
# 4. Close the database connection safely.
#
# Project status:
# - v0.1: Basic energy load analysis with hardcoded station data
# - v0.2: File-based input handling and basic error handling
# - v0.3: CSV import, object-oriented Station model and logging
# - v0.4: PostgreSQL integration with relational station and measurement data
#
# Existing project modules:
# - station.py contains the Station class and object-oriented station logic.
# - read_documents.py contains file and CSV reading logic from previous versions.
# - save_documents.py contains file output logic from previous versions.
# - database.py contains PostgreSQL connection and query logic.
# - output.py contains terminal output formatting for database results.
# - main.py currently controls the PostgreSQL demo/application flow.
#
# Note:
# The CSV/OOP workflow from earlier versions is still part of the project.
# The current v0.4 focus is to add PostgreSQL as the next data backend.
# =============================================================

import logging
logging.basicConfig(filename="app.log", level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s")

from read_documents import read_stations_file
from server import new_stations
from station import Station
from database import fetch_database_report_data
from output import print_database_report

# =============================================================
# Application Startup
# =============================================================

logging.info(f"Program started.\n")

# =============================================================
# Import Station Data from CSV
# =============================================================

doc_name = "stations.csv" # csv document with stations
logging.info(f'Station import from csv file "{doc_name}" started.')

stations = read_stations_file(doc_name) # Read csv file with stations

# =============================================================
# Import Additional Stations from Server
# =============================================================

logging.info('Station import from Server "192.168.178.1" started.')
server_station_count = 0 # Amount of Stations from server

for name, station_data in new_stations.items(): # Import additional Stations from Server
    station = Station.from_server(name, station_data)
    logging.debug(f'{station.name} successfully imported from Server "192.168.178.1"')
    stations.append(station)
    server_station_count += 1

logging.info(f'Successfully imported {server_station_count} stations from Server "192.168.178.1"\n')

# =============================================================
# Generate Station Reports
# =============================================================

logging.info("Station report creation started.")

report = 0
no_report = 0

for station in stations: # Create Report for all stations
    status = station.report()
    if status is True:
        report +=1
    else:
        no_report += 1

logging.info(f"Successfully created report for {report} stations.")
logging.info(f"Report creation for {no_report} stations failed.\n")

# =============================================================
# Load and print Stations & Measurements from PostgreSQL Database
# =============================================================
logging.info("Database report started.")
station_rows, measurement_rows = fetch_database_report_data()
print_database_report(station_rows, measurement_rows)
logging.info("Database report finished.\n")

# =============================================================
# Application Shutdown
# =============================================================

logging.info("Program finished.")

for station in stations:
    print(station)

print(stations)
