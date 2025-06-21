import logging
import os
from config.settings import LOG_FILE_PATH

def setup_logging(name):
    """
    Sets up a consistent logging configuration for the application.
    Logs to console and a file.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO) # Default logging level

    # Ensure log directory exists
    log_dir = os.path.dirname(LOG_FILE_PATH)
    os.makedirs(log_dir, exist_ok=True)

    # Create formatters
    console_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console handler
    if not any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # File handler
    if not any(isinstance(handler, logging.FileHandler) for handler in logger.handlers):
        file_handler = logging.FileHandler(LOG_FILE_PATH)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger 