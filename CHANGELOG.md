# CHANGELOG

## [0.8.0] Update to Use python-ffmpeg for Transcoding
**DATE**: 2024-09-27
- Docker: added pip installation of `python-ffmpeg`.
- tasks: updated the use of `python-ffmpeg` instead of `subprocess` for  
  the transcoding of video files.  
  Added transcoding status updates to debug logging.

## [0.7.1] Add Package Upgrade to Image Build and Fix a Variable
**DATE**: 2024-09-24
- Docker: added `apk upgrade` command after repository update.
- tasks: updated the insert statement with list count.  
  Fixed `DELETE` environment variable with `.lower()` function.

## [0.7.0] Add Options to Retry Failed and Only Update Metadata
**DATE**: 2024-09-22
- Docker: added `CONVERT` and `RETRY_FAILED` environment variables.
- tasks: added `update_metadata` function to only update metadata, no conversions.  
  Added `retry_failed` function to call the `Convert.convert` method again.  
  Updated and organized function names for naming convention  
  to begin with the action.  
  Added `convert_video` function to perform the conversion task itself.
- main: added condition for `CONVERT` value to start converting files ("True"),  
  or only update the metadata ("False").  
  Updated function names changed in tasks.

## [0.6.2] Add Support for Reading Metadata of Large Files
**DATE**: 2024-09-17
- tasks: added "-api largefilesupport" to `read_metadata()` to resolve  
  a false-positive of unknown status for files over 2GB.  
  Cleaned up the exiftool command for readability on multiple lines.

## [0.6.1] Fix Metadata Verification and Typos
**DATE**: 2024-09-15
- tasks: Updated the `verify_metadata()` function to only return  
  the conversion statuses.  
  Updated the `file_type_cmd` entry to add the missing hyphen.

## [0.6.0] Update Metadata Reading and Error Handling [YANKED]
**DATE**: 2024-09-14
- main: moved the metadata debug log out of the function to reduce logging noise.
- tasks: updated the reading of metadata when MP4 files were MKV files  
  with the MP4 file extension.  
  Updated the metadata check within try/except to handle exceptions when the  
  video file is of "data" type.  
  Added "unknown" as status for non-video files.

## [0.5.1] Add Logging for MKV Files
**DATE**: 2024-09-14
- main: added logging of MKV files being added to the conversion queue.  
  MKV files were automatically added but never logged.
- Changelog: changed the format to place the date under the header.

## [0.5.0] Add and Update SQLite Queries for Status Updates
**DATE**: 2024-09-09
- main: updated SQL queries to check for status field.  
  Added a call to the `final_count()` fuction at the end of all conversions.
- tasks: added a `status_update` function for setting and changing the status.  
  Added the status field to the SQL queries to ensure the selected  
  file is queued, and updated to "active" during the conversion stage.  
  Updated the values on convert to be "Y" or "N" TEXT (no BOOL in SQLite)  
  and status value of "skip" to "skipped".  
  Changed the original values to "skipped" or "Y/N" as necessary.  
  Added a `final_count()` function to log the total results of the last run.
- schema: updated status to "skipped" default value, and  
  changing the default convert value to "N" for boolean-type values.

## [0.4.1] Add SQLite Package
**DATE**: 2024-09-07
- Docker: added sqlite package installation to use for troubleshooting  
  any issues with the SQLite database.

## [0.4.0] Create a User and Add Config for SQLite Database and Log File
**DATE**: 2024-09-06
- Docker: added a user to run the conversion tool, and have its UID and GID  
  match the ownership of the mounted volume via *docker-compose.yaml*.  
  Fixed the syntax in the *docker-compose.yaml* file.
- config: added a configuration file for the temporary storage of the  
  SQLite database and the logging file.
- interfaces: updated to use the temporary storage location.
- main: updated to use the temporary storage location.

## [0.3.4] Minor Change for Calling BATCH Environment Variable
**DATE**: 2024-08-24
- tasks: used `os.getenv()` instead of `os.environ[]` for the 'BATCH' environment  
  variable, to set a default value of "0" (string zero).  
  `os.getenv()` returns a string, per [PLW1508](https://docs.astral.sh/ruff/rules/invalid-envvar-default/).

## [0.3.3] Add Log File to Repository
**DATE**: 2024-08-24
- logs: this was built into the Docker image. However, since the file is created by  
  the module, it relies on the existence of the 'logs' directory.  
  The 'logs' directory and 'convert.log' file are now part of the repository.

## [0.3.2] Minor Change to Docker Image Name and Cleanup Logging
**DATE**: 2024-08-24
- Changed the docker image name from an underscore (`_`) to a hyphen (`-`).
- tasks.delete_original: consolidated the cleanup logging messages for MKV and MP4.

## [0.3.1] Feature: Setup non-root User Environment
**DATE**: 2024-08-24
- Docker: add the `UID` and `GID` environment variables to set the output file  
  ownership. This variable is set in the **docker-compose.yaml** file.

## [0.3.0] Feature: Add File Size Reporting
**DATE**: 2024-08-19
- tasks.get_file_size: added a function to check the file size, logging the  
  size in a human-readable value, and returning the size in bytes.
- tasks.Convert.convert: implemented the usage of the function to calculate the  
  amount of disk space that was recovered by converting to h.265 HVC1,  
  or can be recovered, if `DELETE` was set to "False".

## [0.2.2] Minor Updates to Logging
**DATE**: 2024-08-16
- tasks.scan_sql_insert: added an exception for `IntegrityError` raised when  
  a duplicate filename is being inserted into the table. This is a specific  
  error, compared to being captured from a generic `Error` exception.  
  Removed unnecessary return.
- Using the `.exception()` logging will provide a traceback, and is  
  not always required, such as `IntegrityError`. Removed unnecessary  
  exception logging to reduce the traceback noise. Applied to all files.
- Removed more excessive and redundant debug logging.
- `main` file: minor cleanup of the grouped tasks between scanning and converting.
- Docker: added `TZ` environment variable to set the timezone for log file timestamp.

## [0.2.1] HOT-FIX: Remove SQLite Update Limit
**DATE**: 2024-08-16
- tasks.Convert.convert: remove `LIMIT 1;` from the status update  
  SQLite statement. This is a syntax issue, raising sqlite3.OperationalError.

## [0.2.0] Add SQL Status Update
**DATE**: 2024-08-15
- tasks.Convert.convert: add a `finally` entry after the conversion  
  task. Successful conversions are "done" and unsuccessful conversions  
  are "failed" status. The status is also the method return value,  
  which is used for (dis)allowing the deletion of the original file.

## [0.1.2] Bug Fix: Variable Error
**DATE**: 2024-08-15
- tasks.convert_batch: used the wrong variable name.  
  Fixed call to `{batch}` instead of `{limit}`.
- v0.1.1 is yanked from Docker Hub.

## [0.1.1] Bug Fix: Logging [YANKED]
**DATE**: 2024-08-15
- Logging was inconsistent, and setup with different logger names.  
  Some of the logging is repetitive, between the function and callable.  
  Updated the logging message format, quoted filename variables, and  
  improved messages for readability.
- Added a heading to the changelog entries, and updated format layout.
- tasks.convert_batch: using `int(batch)` was redundant; type was checked.
- tasks.read_metadata: change the convert status to "skip" if it's HVC1.

## [0.1.0] Change to Base Image
**DATE**: 2024-08-14
- Docker image changed from "python:3.12-slim" to "python:3.12-alpine3.20".  
  The original image was based on Debian Bookworm, and 862MB in size.  
  The new image is based on Alpine Linux, and the size is now 277MB.

## [0.0.1] Initial Release
**DATE**: 2024-08-14
- First official release of the h.265 converter tool.  
  Refer to the [README](README.md) for usage and general information.
