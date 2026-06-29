# ============================================================
# Energy Operations Platform
#
# Current development focus: v0.5
#
# This script represents the existing PostgreSQL-based
# application flow and remains part of the project backend
# foundation.
#
# Current v0.5 transition:
# 1. Keep the PostgreSQL data access and terminal output flow stable.
# 2. Introduce FastAPI as a new API layer in api.py.
# 3. Prepare existing database result mappings for JSON responses.
# 4. Move step by step from terminal-based output to REST endpoints.
#
# Project status:
# - v0.1: Basic energy load analysis with hardcoded station data
# - v0.2: File-based input handling and basic error handling
# - v0.3: CSV import, object-oriented Station model and logging
# - v0.4: PostgreSQL integration with relational station and measurement data
# - v0.4.1: Database results mapped into dictionaries for JSON/API preparation
# - v0.5: FastAPI entry point with first health and API test endpoints
#
# Current application structure:
# - main.py controls the PostgreSQL-based terminal demo/application flow.
# - database.py contains PostgreSQL connection and query logic.
# - output.py contains terminal output formatting for database results.
# - api.py contains the new FastAPI application and REST endpoints.
#
# Existing project modules:
# - station.py contains the Station class and object-oriented station logic.
# - read_documents.py contains file and CSV reading logic from previous versions.
# - server.py contains simulated additional station data from a server source.
# - legacy_csv_demo.py preserves the previous CSV/OOP workflow from v0.3.
#
# Note:
# The current v0.5 focus is the transition from a PostgreSQL-backed
# terminal application to a FastAPI-backed backend service. The existing
# main.py flow remains useful for testing and understanding the database
# layer while the API layer is developed separately in api.py.
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