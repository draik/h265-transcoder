"""Defines all of the jobs and shared functions."""

import logging
import os
import sqlite3
import subprocess
from pathlib import Path

from h265_converter.interfaces import DatabaseInterface

logger = logging.getLogger("app")
BATCH = os.environ["BATCH"]


class Convert:
    """Instantiate the video file for editing."""
    def __init__(self, path: str, filename: str):
        """Setup the path and filename instance for video conversion.

        Args:
            path (str): the absolute path to the video file.
            filename (str): the video filename.
        """
        self.filename = filename
        self.path = path
        self.input_file = f"{self.path}/{self.filename}"
        if self.filename.endswith(".mkv"):
            self.output_file = self.input_file.replace(".mkv", ".mp4")
            self.video_title = self.filename.removesuffix(".mkv")
        elif self.filename.endswith(".mp4"):
            self.output_file = self.input_file.replace(".mp4", ".h265")
            self.video_title = self.filename.removesuffix(".mp4")

        initiate_msg = f"Initiating '{filename}' conversion."
        logger.info(initiate_msg)


    def convert(self) -> str:
        """Convert video file to h.265 HVC1 MP4.

        During the conversion, metadata will be cleaned up.
        Title tag will match the filename without an extension.
        Comment tag will be cleared.

        Returns:
            0 - Conversion was successful.
            Any non-zero value is a failed conversion.
        """
        convert_cmd = ["/usr/bin/ffmpeg",
                        "-i", f"{self.input_file}",
                        "-c:v", "libx265",
                        "-vtag", "hvc1",
                        "-c:a", "copy",
                        "-metadata", f"title={self.video_title}",
                        "-metadata", "comment=",
                        "-f", "mp4",
                        f"{self.output_file}"]
        convert_cmd_msg = f"{convert_cmd=}"
        logger.debug(convert_cmd_msg)
        try:
            convert_msg = f"Converting '{self.input_file}' to '{self.output_file}'."
            logger.info(convert_msg)
            subprocess.run(convert_cmd,
                           capture_output=True,
                           check=True,
                           text=True)
        except subprocess.CalledProcessError:
            convert_err_msg = f"Failed to convert '{self.input_file}'"
            logger.error(convert_err_msg)
            logger.exception(subprocess.CalledProcessError)
            if Path(self.output_file).exists():
                logger.debug("Removing the failed output file.")
                Path(self.output_file).unlink()
                logger.debug("Removed output file.")
            else:
                cleanup_msg = f"Nothing to remove. '{self.output_file}' not found."
                logger.debug(cleanup_msg)
            convert_status = "failed"
        else:
            success_msg = f"'{self.input_file}' converted successfully."
            logger.info(success_msg)
            convert_status = "done"
        finally:
            status_update_query = """UPDATE queue
                                        SET status = ?
                                        WHERE path = ? AND
                                        filename = ?
                                        LIMIT 1;"""
            status_update_data = (convert_status, self.path, self.filename)
            with DatabaseInterface() as (_connect, db_cursor):
                try:
                    db_cursor.execute(status_update_query, status_update_data)
                except sqlite3.Error:
                    logger.error("SQLite status update failed.")
                    logger.exception(sqlite3.Error)
                else:
                    db_cursor.close()
                    sql_update_msg = f"Updated status for '{self.filename}' to '{convert_status}'."
                    logger.info(sql_update_msg)
        return convert_status


    def delete_original(self) -> None:
        """Remove the original input file.

        MKV conversion outputs to MP4 file, and the original MKV will be deleted.
        MP4 conversion outputs to ".h265" MP4, which will overwrite the ".mp4" file.
        """
        if self.input_file.endswith(".mkv"):
            cleanup_msg = f"Deleting '{self.input_file}'."
            logger.info(cleanup_msg)
            Path(self.input_file).unlink()
        elif self.input_file.endswith(".mp4"):
            cleanup_msg = f"Renaming '{self.output_file}' to '{self.input_file}'."
            logger.info(cleanup_msg)
            Path(self.output_file).replace(self.input_file)
        logger.info("Conversion cleanup complete.")


def convert_batch() -> list:
    """Obtain a list of files to convert based on batch limit.

    Returns:
        List of tuples containing the '(path, filename)' of files to convert.
    """
    try:
        batch = int(BATCH)
    except ValueError:
        value_error_msg = f"BATCH is not an integer. {BATCH=}"
        logger.warning(value_error_msg)
        logger.info("Setting batch to unlimited.")
        limit = None
    else:
        if batch == 0:
            logger.info("Batch is 0; unlimited.")
            limit = None
        elif batch > 0:
            batch_msg = f"Setting batch limit to {batch}."
            logger.debug(batch_msg)
            limit = batch
        elif batch < 0:
            batch_msg = f"{batch=}. BATCH variable must be a positive number."
            logger.debug(batch_msg)
            negative_msg = f"Batch is '{batch}'; unlimited."
            logger.info(negative_msg)
            limit = None
        else:
            limit = None

    batch_query = "SELECT path, filename FROM queue WHERE convert = 'convert' ;"
    if limit:
        batch_query = batch_query.replace(";", f"LIMIT {limit} ;")
    with DatabaseInterface() as (_connect, db_cursor):
        try:
            batch_result = db_cursor.execute(batch_query)
            batch_queue = batch_result.fetchall()
        except sqlite3.Error:
            logger.error("SQLite query failed.")
            logger.exception(sqlite3.Error)
            raise SystemExit(1) from sqlite3.Error
        else:
            db_cursor.close()
            logger.info("Successfully retrieved batch list.")
            return batch_queue


def path_scanner() -> list:
    """Scan for video files.

    Creates a tuple of the absolute path and filename,
    then appends to the list of the scan results.

    Returns:
        List of tuples containing the absolute path and filename.
    """
    scan_path = "/mnt"
    video_extensions = (".mkv", ".mp4")
    video_list = []

    logger.debug("Beginning scan...")
    for root, _dirs, files in os.walk(scan_path):
        for filename in files:
            if filename.endswith(video_extensions):
                video_list.append((root, filename))
                found_msg = f"Found '{root}/{filename}'."
                logger.info(found_msg)
    logger.debug("Scan complete.")
    scan_results_msg = f"Found {len(video_list)} video files."
    logger.info(scan_results_msg)
    if len(video_list) == 0:
        logger.warning("Empty scan results. Is the volume mounted? Exiting.")
        raise SystemExit(1)
    return video_list


def read_metadata(path: str, filename: str) -> tuple:
    """Read video file metadata for Compressor ID.

    Args:
        path (str): Absolute path to the video file.
        filename (str): Filename for the video.

    Returns:
        Tuple of the filename and conversion status.
    """
    video_file = f"{path}/{filename}"
    logger.debug("Checking Compressor ID metadata.")
    reader_cmd = ["/usr/bin/exiftool", "-s3", "-CompressorID", video_file]
    metadata_sp = subprocess.run(reader_cmd,
                                 capture_output = True,
                                 check = True,
                                 text = True)
    if metadata_sp.stdout.lower().strip() == "hvc1":
        converted_msg = f"'{video_file}' is already converted."
        logger.info(converted_msg)
        result = (filename, "skip")
    elif metadata_sp.stdout == "":
        unknown_msg = f"'{video_file}' returned empty Compressor ID. Verify video integrity."
        logger.warning(unknown_msg)
        result = (filename, "skip")
    else:
        convert_msg = f"'{video_file}' needs to be converted."
        logger.info(convert_msg)
        result = (filename, "convert")
    return result


def scan_sql_insert(insert_list: list) -> int:
    """Insert scan results list into SQLite database.

    The list contains a list of values for the SQL insert.

    Returns:
        0 - SQL insertion was successful.
        Any non-zero value is a failure to execute the SQL insertion.
    """
    insert_statement = """INSERT INTO queue (
                            path, filename, convert)
                        VALUES (
                            ?, ?, ?);
    """

    logger.debug("Inserting scanned results into SQLite 'queue' table.")

    with DatabaseInterface() as (_connect, db_cursor):
        try:
            db_cursor.executemany(insert_statement, insert_list)
        except sqlite3.Error:
            logger.error("SQLite execution failed.")
            logger.exception(sqlite3.Error)
            raise SystemExit(1) from sqlite3.Error
        else:
            db_cursor.close()
            logger.info("Successfully inserted list into SQLite 'queue' table.")
            return 0


def setup_database(schema_file: str) -> int:
    """Setup the SQLite database.

    Returns:
        0 - successfully import schema_file into SQLite DB.
        Any non-zero value is a failure to import the schema_file.
    """
    logger.debug("Setting up the SQLite database...")

    try:
        with Path(schema_file).open(mode="r", encoding="utf-8") as db_schema:
            create_table = db_schema.read()
    except FileNotFoundError:
        file_not_found_msg = f"{schema_file} was not found."
        logger.error(file_not_found_msg)
        logger.exception(FileNotFoundError)
        raise SystemExit(1) from FileNotFoundError
    else:
        with DatabaseInterface() as (connection, cursor):
            cursor.executescript(create_table)
            cursor.close()
        logger.debug("SQLite database setup complete.")
        return 0
