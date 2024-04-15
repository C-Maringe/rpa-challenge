import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def create_logger(logger_name):
    # Create a custom logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # Set the logger level to DEBUG

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Define log file path
    log_file_path = f"{logger_name}.log"

    # Ensure log file directory exists
    log_file_directory = Path(log_file_path).parent
    log_file_directory.mkdir(parents=True, exist_ok=True)

    # Create a file handler
    file_handler = RotatingFileHandler(filename=log_file_path, mode='a', maxBytes=5 * 1024 * 1024,
                                       backupCount=2, encoding='utf-8', delay=False)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Create a stream handler (for printing to the terminal)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)  # Set the handler level to INFO
    stream_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
