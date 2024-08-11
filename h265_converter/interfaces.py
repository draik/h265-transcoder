"""Contains the SQLite database connection class."""

import logging
import sqlite3

logger = logging.getLogger(__name__)


class DatabaseInterface:
    """Setup the SQLite database.

    Ensure the SQLite database file is created, and a cursor is available.
    """
    def __init__(
        self
    ):
        """Create the SQLite database."""
        logger.debug("Initializing DatabaseInterface...")
        self.db_file = "queue.db"

        self.db_connect = None
        self.db_cursor = None

    def __enter__(self) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
        """Connects to the database, and returns the connection and cursor."""
        try:
            self.db_connect = sqlite3.connect(self.db_file)
            self.db_cursor = self.db_connect.cursor()
        except sqlite3.Error:
            logger.exception("Failed to connect to the database.")
            raise SystemExit(1) from sqlite3.Error

        return self.db_connect, self.db_cursor

    def __exit__(self, exception_type, exception_value, exception_traceback) -> None:
        """Closed the database connection."""
        logger.debug("Closing the database connection...")

        if exception_type:
            exception_msg = f"An exception occurred: {exception_type}, {exception_value}"
            logger.error(exception_msg)

        self.db_connect.commit()
        self.db_connect.close()
        logger.debug("Database connection closed.")
