"""Contains the entrypoint for the h.265 conversion tool."""

import logging
import os
import sys

from h265_converter import tasks

DEBUG = os.environ["DEBUG"].lower()
DELETE = os.environ["DELETE"].lower()
app_root = "/app/h265_converter"
log_file = f"{app_root}/logs/convert.log"
schema_file = f"{app_root}/schema.sql"

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
scan_list = tasks.path_scanner()

queue_list = []
for result in scan_list:
    path = result[0]
    filename = result[1]
    if filename.endswith(".mkv"):
        queue_list.append([path, filename, "convert"])
    else:
        filename, convert = tasks.read_metadata(path, filename)
        queue_list.append([path, filename, convert])

tasks.scan_sql_insert(queue_list)

convert_list = tasks.convert_batch()
if not convert_list:
    logger.warning("No files marked for conversion. Exiting.")
    raise SystemExit(1)

for queue in convert_list:
    path = queue[0]
    filename = queue[1]
    video_file = tasks.Convert(path, filename)
    convert_video = video_file.convert()
    if (convert_video == "done") and (DELETE == "true"):
        video_file.delete_original()
