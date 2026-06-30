from pathlib import Path
import logging

def configure_logging():
    """Configure application logging and create the local log directory if needed."""

    Path("logs").mkdir(exist_ok=True)

    logging.basicConfig(filename="logs/app.log", level=logging.DEBUG,
                        format="%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s")
    
    # Reduce noisy server and reload logs in the application log file.
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("watchfiles").setLevel(logging.WARNING)