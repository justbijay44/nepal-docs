import logging
import os
from datetime import datetime

LOG_DIRS = "logs"
os.makedirs(LOG_DIRS, exist_ok=True)

log_filename = os.path.join(LOG_DIRS, f"{datetime.now().strftime('%Y-%m-%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

def get_logger(name):
    return logging.getLogger(name)

logger = get_logger(__name__)