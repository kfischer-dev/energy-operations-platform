"""
Terminal entry point for the PostgreSQL-based database report.

The FastAPI application is defined separately in src/api.py.
This module keeps the original terminal workflow available for testing
and learning while the REST API layer is developed.
"""

import logging
from src.logging_config import configure_logging

from src.database import fetch_database_report_data
from src.output import print_database_report

configure_logging()

# =============================================================
# Application Startup
# =============================================================

logger = logging.getLogger(__name__)
logger.info("=" * 60)
logger.info(f"Program started.")

# =============================================================
# Load and print Stations & Measurements from PostgreSQL Database
# =============================================================

logger.info("Database report started.")
station_data, measurement_data = fetch_database_report_data()
print_database_report(station_data, measurement_data)
logger.info("Database report finished.")

# =============================================================
# Application Shutdown
# =============================================================

logger.info("Program finished.")
logger.info("=" * 60)