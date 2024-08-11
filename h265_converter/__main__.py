"""Contains the entrypoint for the h.265 conversion tool."""

import logging
import os

import tasks

logger = logging.getLogger(__name__)

# Logging to stdout will show all levels
stdout_handler = logging.StreamHandler()
stdout_handler.setLevel("DEBUG")
stdout_format = logging.Formatter("[%(name)s::%(levelname)s - %(message)s")
stdout_handler.setFormatter(stdout_format)
logger.addHandler(stdout_handler)

# Logging to a file defaults to INFO
file_handler = logging.FileHandler("/app/logs/convert.log", mode="a", encoding="utf-8")
if os.environ["DEBUG"]:
    file_handler.setLevel("DEBUG")
else:
    file_handler.setLevel("INFO")
file_format = logging.Formatter("%(asctime)s [%(name)s::%(levelname)s - %(message)s]")
file_handler.setFormatter(file_format)
logger.addHandler(file_handler)

# Setup SQLite database
logger.debug("Initializing SQLite database...")
tasks.setup_database("schema.sql")
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
    logger.info("No files marked for conversion. Exiting.")
    raise SystemExit(1)

for queue in convert_list:
    path = queue[0]
    filename = queue[1]
    convert_video = tasks.Convert(path, filename)
    convert_video.convert()
