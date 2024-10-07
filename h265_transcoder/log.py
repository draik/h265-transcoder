import logging
import os
import sys
from pathlib import Path

from h265_transcoder import config

log_file = Path(config.temp_dir.name) / config.log_filename
DEBUG = bool(os.environ["DEBUG"].lower() == "true")
TRANSCODE = 5

logger = logging.getLogger("app")
logging.addLevelName(TRANSCODE, "TRANSCODE")


def transcode(self, message, *args, **kwargs):
    if self.isEnabledFor(TRANSCODE):
        self._log(TRANSCODE, message, args, **kwargs)


logging.Logger.transcode = transcode
logger.setLevel(TRANSCODE)

# Logging to stdout will show all levels
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel("TRANSCODE")
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
