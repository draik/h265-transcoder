"""Contains the entrypoint for the h.265 conversion tool."""

import logging
import os
import sys
from pathlib import Path

from h265_converter import config, tasks

CONVERT = bool(os.environ["CONVERT"].lower() == "true")
DEBUG = bool(os.environ["DEBUG"].lower() == "true")
PERSIST = bool(os.environ["PERSIST"].lower() == "true")
RETRY_FAILED = bool(os.environ["RETRY_FAILED"].lower() == "true")

log_file = Path(config.temp_dir.name) / config.log_filename

logger = logging.getLogger("app")
logger.setLevel("DEBUG")

# Logging to stdout will show all levels
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel("DEBUG")
stdout_format = logging.Formatter("[{levelname}] {message}", style="{")
stdout_handler.setFormatter(stdout_format)
logger.addHandler(stdout_handler)

# Logging to a file defaults to INFO
file_handler = logging.FileHandler(filename=log_file, mode="a", encoding="utf-8")
if DEBUG:
    file_handler.setLevel("DEBUG")
else:
    file_handler.setLevel("INFO")
file_format = logging.Formatter("{asctime} [{levelname}] {message}",
                                datefmt="%Y-%m-%d %H:%M:%S",
                                style="{",)
file_handler.setFormatter(file_format)
logger.addHandler(file_handler)

# Setup SQLite database
sqlite_db = ""
if PERSIST:
    sqlite_db = config.persist_db
    queue_count = tasks.verify_database()
    if queue_count == 0:
        empty_table_msg = f"SQLite DB '{sqlite_db}' is empty. Setting up."
        logger.info(empty_table_msg)
        tasks.scan_directory(sqlite_db)
    else:
        queue_msg = f"Found {queue_count} video files in queue."
        logger.info(queue_msg)
else:
    sqlite_db = Path(config.temp_dir.name) / config.temp_db
    temp_db_msg = f"Setting up temporary SQLite database at '{sqlite_db}'"
    logger.debug(temp_db_msg)
    tasks.setup_database(sqlite_db)
    tasks.scan_directory(sqlite_db)

# Convert the failed video files in queue
if PERSIST and RETRY_FAILED:
    logger.info("Retrying failed video files.")
    retry_transcoding = tasks.retry_failed(sqlite_db)
    if retry_transcoding:
        tasks.convert_queue(sqlite_db, retry_transcoding)

# Convert the video file or only update the metadata
if CONVERT:
    convert_list = tasks.get_batch(sqlite_db)
    if convert_list:
        tasks.convert_queue(sqlite_db, convert_list)
        if RETRY_FAILED:
            retry_conversion = tasks.retry_failed(sqlite_db)
            if retry_conversion:
                tasks.convert_queue(sqlite_db, retry_conversion)
    else:
        logger.warning("No video files to convert. Exiting.")
else:
    tasks.update_metadata(sqlite_db)

# Output the status count
tasks.final_results(sqlite_db)
