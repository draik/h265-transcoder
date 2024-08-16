# CHANGELOG

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
  Refer to the README.md for usage and general information.