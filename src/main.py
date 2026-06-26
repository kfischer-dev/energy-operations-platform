# ============================================================
# Energy Operations Platform
#
# Current development focus: v0.4
#
# This script starts the current PostgreSQL-based application flow:
# 1. Load station and measurement data from PostgreSQL.
# 2. Use relational data from the stations and measurements tables.
# 3. Print the retrieved database report to the terminal.
# 4. Keep database access, output formatting and application flow separated.
#
# Project status:
# - v0.1: Basic energy load analysis with hardcoded station data
# - v0.2: File-based input handling and basic error handling
# - v0.3: CSV import, object-oriented Station model and logging
# - v0.4: PostgreSQL integration with relational station and measurement data
#
# Current application flow:
# - main.py controls the PostgreSQL-based v0.4 demo/application flow.
# - database.py contains PostgreSQL connection and query logic.
# - output.py contains terminal output formatting for database results.
#
# Existing project modules:
# - station.py contains the Station class and object-oriented station logic.
# - read_documents.py contains file and CSV reading logic from previous versions.
# - server.py contains simulated additional station data from a server source.
# - legacy_csv_demo.py preserves the previous CSV/OOP workflow from v0.3.
#
# Note:
# The earlier CSV/OOP workflow is still part of the project history and can
# be run separately through legacy_csv_demo.py. The current v0.4 focus is the
# transition from CSV-based processing to a PostgreSQL-backed data backend.
# ============================================================

import logging
logging.basicConfig(filename="app.log", level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s")

from src.database import fetch_database_report_data
from src.output import print_database_report

# =============================================================
# Application Startup
# =============================================================

logging.info(f"Program started.\n")

# =============================================================
# Load and print Stations & Measurements from PostgreSQL Database
# =============================================================

logging.info("Database report started.")
station_data, measurement_data = fetch_database_report_data()
print_database_report(station_data, measurement_data)
logging.info("Database report finished.\n")

# =============================================================
# Application Shutdown
# =============================================================

logging.info("Program finished.")