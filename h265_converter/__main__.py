"""Contains the entrypoint for the h.265 conversion tool."""

import logging
import os
import sys
from pathlib import Path

from h265_converter import config, tasks

CONVERT = os.environ["CONVERT"].lower()
DEBUG = os.environ["DEBUG"].lower()
RETRY_FAILED = os.environ["RETRY_FAILED"].lower()

log_file = Path(config.temp_dir.name) / config.log_filename
db_file = Path(config.temp_dir.name) / config.db_filename
schema_file = "/app/h265_converter/schema.sql"

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
if DEBUG == "true":
    file_handler.setLevel("DEBUG")
else:
    file_handler.setLevel("INFO")
file_format = logging.Formatter("{asctime} [{levelname}] {message}",
                                datefmt="%Y-%m-%d %H:%M:%S",
                                style="{",)
file_handler.setFormatter(file_format)
logger.addHandler(file_handler)

# Setup SQLite database
tasks.setup_database(schema_file)
logger.info("SQLite database is ready.")

# Scan for video files to convert
scan_list = tasks.scan_directory()
logger.debug("Checking metadata on video files.")
queue_list = []
for result in scan_list:
    path = result[0]
    filename = result[1]
    if filename.endswith(".mkv"):
        convert_msg = f"'{path}/{filename}' needs to be converted."
        logger.info(convert_msg)
        queue_list.append([path, filename, "Y", "queued"])
    else:
        filename, convert, status = tasks.read_metadata(path, filename)
        queue_list.append([path, filename, convert, status])
tasks.insert_scan_results(queue_list)

# Convert the video file or only update the metadata
if CONVERT == "true":
    convert_list = tasks.get_batch()
    if convert_list:
        tasks.convert_queue(convert_list)
        if RETRY_FAILED == "true":
            retry_conversion = tasks.retry_failed()
            if retry_conversion:
                tasks.convert_queue(retry_conversion)
    else:
        logger.warning("No video files found. Exiting.")
        raise SystemExit(1)
else:
    tasks.update_metadata()

# Output the status count
tasks.final_count()
