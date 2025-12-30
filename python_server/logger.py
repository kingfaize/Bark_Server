import logging
import os
from .config import Config

# Determine the path for the log file (project root)
LOG_FILE_PATH = os.path.join(Config.PROJECT_ROOT, "log.log")

# Ensure the log file exists and directories are created
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
if not os.path.exists(LOG_FILE_PATH):
    with open(LOG_FILE_PATH, "a") as f:
        pass

# Configure the logger
logger = logging.getLogger("bark_server")
logger.setLevel(logging.DEBUG)

# File handler (writes to log.log)
file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

# Console handler (optional, for stdout)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers if not already added
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# --- Intercept External Loggers ---
# This ensures that Uvicorn and FastAPI system logs (errors, startup, access) 
# also get written to our log.log file.
external_loggers = ["uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"]
for logger_name in external_loggers:
    ext_logger = logging.getLogger(logger_name)
    ext_logger.addHandler(file_handler)
    # Optional: ensure they are at least INFO level
    ext_logger.setLevel(logging.INFO)

# Example usage:
# logger.debug("Debug message")
# logger.info("Info message")
# logger.warning("Warning message")
# logger.error("Error message")
