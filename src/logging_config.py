from pathlib import Path
import logging

def configure_logging():
    Path("logs").mkdir(exist_ok=True)

    logging.basicConfig(filename="logs/app.log", level=logging.DEBUG,
                        format="%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s")
    
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("watchfiles").setLevel(logging.WARNING)