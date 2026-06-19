# =============================================================
# Energy Monitoring Platform - v0.32
# -------------------------------------------------------------
#
# Changelog
#
# New Features:
# - Introduced Python logging framework
# - Centralized logging configuration
# - Structured application logging
# - CSV import monitoring
# - Server import monitoring
# - Data validation logging
# - Report generation logging
# - Replaced custom error reporting with logging
#
# Architecture:
# - main.py            -> Application control & logging configuration
# - read_documents.py  -> CSV data source
# - server.py          -> Simulated server data source
# - station.py         -> Domain model, business logic & validation
#
# =============================================================

import logging
logging.basicConfig(filename="app.log", level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s")

from read_documents import read_stations_file
from server import new_stations
from station import Station

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
# Application Shutdown
# =============================================================

logging.info("Program finished.")

for station in stations:
    print(station)

print(stations)
