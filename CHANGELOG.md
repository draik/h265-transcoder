# CHANGELOG

## [0.3.2] Minor Change to Docker Image Name and Cleanup Logging
- Changed the docker image name from an underscore (`_`) to a hyphen (`-`).
- tasks.delete_original: consolidated the cleanup logging messages for MKV and MP4.

## [0.3.1] Feature: Setup non-root User Environment
- Docker: add the `UID` and `GID` environment variables to set the output file  
  ownership. This variable is set in the **docker-compose.yaml** file.

## [0.3.0] Feature: Add File Size Reporting
- tasks.get_file_size: added a function to check the file size, logging the  
  size in a human-readable value, and returning the size in bytes.
- tasks.Convert.convert: implemented the usage of the function to calculate the  
  amount of disk space that was recovered by converting to h.265 HVC1,  
  or can be recovered, if `DELETE` was set to "False".

## [0.2.2] Minor Updates to Logging
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
- tasks.Convert.convert: remove `LIMIT 1;` from the status update  
  SQLite statement. This is a syntax issue, raising sqlite3.OperationalError.

## [0.2.0] 2024-08-15 Add SQL Status Update
- tasks.Convert.convert: add a `finally` entry after the conversion  
  task. Successful conversions are "done" and unsuccessful conversions  
  are "failed" status. The status is also the method return value,  
  which is used for (dis)allowing the deletion of the original file.

## [0.1.2] 2024-08-15 Bug Fix: Variable Error
- tasks.convert_batch: used the wrong variable name.  
  Fixed call to `{batch}` instead of `{limit}`.
- v0.1.1 is yanked from Docker Hub.

## [0.1.1] 2024-08-15 Bug Fix: Logging [YANKED]
- Logging was inconsistent, and setup with different logger names.  
  Some of the logging is repetitive, between the function and callable.  
  Updated the logging message format, quoted filename variables, and  
  improved messages for readability.
- Added a heading to the changelog entries, and updated format layout.
- tasks.convert_batch: using `int(batch)` was redundant; type was checked.
- tasks.read_metadata: change the convert status to "skip" if it's HVC1.

## [0.1.0] 2024-08-14 Change to Base Image
- Docker image changed from "python:3.12-slim" to "python:3.12-alpine3.20".  
  The original image was based on Debian Bookworm, and 862MB in size.  
  The new image is based on Alpine Linux, and the size is now 277MB.

## [0.0.1] 2024-08-14 Initial Release
- First official release of the h.265 converter tool.  
  Refer to the [README](README.md) for usage and general information.
