"""Contains the entrypoint for the h.265 transcoding tool."""

import logging
import os
from pathlib import Path

from h265_transcoder import config, log, tasks

TRANSCODE = bool(os.environ["TRANSCODE"].lower() == "true")
PERSIST = bool(os.environ["PERSIST"].lower() == "true")
RETRY_FAILED = bool(os.environ["RETRY_FAILED"].lower() == "true")

logger = logging.getLogger("app")
logger.setLevel(log.TRANSCODE)

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

# Transcode the failed video files in queue
if PERSIST and RETRY_FAILED:
    logger.info("Retrying failed video files.")
    retry_transcoding = tasks.retry_failed(sqlite_db)
    if retry_transcoding:
        tasks.transcode_queue(sqlite_db, retry_transcoding)

# Transcode the video file or only update the metadata
if TRANSCODE:
    transcode_list = tasks.get_batch(sqlite_db)
    if transcode_list:
        tasks.transcode_queue(sqlite_db, transcode_list)
        if RETRY_FAILED:
            retry_transcoding = tasks.retry_failed(sqlite_db)
            if retry_transcoding:
                tasks.transcode_queue(sqlite_db, retry_transcoding)
    else:
        logger.warning("No video files to transcode. Exiting.")
else:
    tasks.update_metadata(sqlite_db)

# Output the status count
tasks.final_results(sqlite_db)
