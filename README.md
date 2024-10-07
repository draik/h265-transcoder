# H.265 Transcoder

## Description
Scan a directory for video files that need to be transcoded to h.265 HVC1 MP4 format, and process the findings. These are possible scan results:

* MKV (transcode) - All MKV will be transcoded to MP4 even if it's h.265 HVC1
* MP4 (transcode) - Transcode MP4 if not h.265 HVC1
* MP4 (skip) - MP4 is already h.265 HVC1

### CAVEAT
The transcoding is for **ONE** video stream (video track 0, usually track 0) and **ONE** audio stream (audio track 0, usually track 1). If the file has multiple audio tracks (i.e.: anime dubs), it may choose the wrong language, as there is no standard for ordering tracks. Furthermore, as this will only use those two tracks, all others will be ignored, including subtitles. Extract any subtitles with `mkvextract` prior to transcoding as original files can be deleted after a successful transcoding (see "Environment Variables" below).

## How It Works
Once the container starts, it scans the mounted volume for video files to transcode and update metadata. If no files are found, or nothing to transcode, the container will shut itself down. The found files will be inserted into the SQLite database, and queued for processing. After scans are complete, the transcoding will begin for files with a *transcode* value. Transcoded results will be *failed* or *done*.  

During the transcoding process, the output file will have the *Title* metadata updated to match the filename (without extension), and the *Comment* tag removed.

![Workflow diagram](workflow_diagram.png)

## Docker

### Pull the image
The image is available on [Docker Hub](https://hub.docker.com/r/draikx21/h265-transcoder/):

`docker pull draikx21/h265-transcoder`

### Build an Image
Build the docker image using the following command:

`docker build -f docker/Dockerfile [-t <image_name:tag>] .`

### Run a Container
***DOCKER COMPOSE***  
Use the provided **docker-compose.yaml** file, and ensure the variables are properly set. Additionally, set the local directory to scan is mounted to "/mnt" within the container.

***MANUALLY***  
All variables and volumes are specified at the time of execution.

`docker run [-u uid:gid] [-e key=value] -v /path/to/videos:/mnt <image_name[:tag]>`

### Environment Variables

***UID*** and ***GID*** (default = 1000)  
This setting is in the **docker-compose.yaml** file. When this is set with the corresponding UID (user ID) and GID (group ID) as the source file user, it will ensure the output file matches the ownership. Without it, all content is owned by the Docker container's root user (UID and GID 0). To obtain the user's UID and GID from the command line, use the `id` command. By itself, it will provide your user's information, and `id <username>` will provider information on the specified user.  
*Note*: The username does not matter for the environment variable, only the UID and GID.

***BATCH*** (default = 0)  
This is for the amount of video files to transcode. The default value is "0" (zero) which is unlimited, and will go through all of the video files it found in the scan. The list depends on the result order from the `os.walk` scan, as the limit is for the top batch count.

:exclamation: Be mindful of the resource usage, and overworking your machine for long periods of video transcoding.

***DEBUG***  (default = "False")  
Pertains to the log file, not stdout logging. It will log all INFO-level and higher messages. Set the value to "True" to enable DEBUG-level stdout logging. 

***DELETE*** (default = "False")  
Once a video file has been successfully transcoded to h.265, the original file can be removed. Set value to "True" to enable this action.

***TZ*** (default = "UTC")  
Set the timezone for logging to the file. The list of TZ Identifiers which can be used in place of "UTC" can be found on [Wikipedia](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

### Reading the Docker Logs (stdout logging)
The console output is setup with DEBUG-level logging. While the Docker container is running, the console will display the current actions, but all console output is available in the Docker logs, even after it shuts down (and container is not removed). Read the Docker logs with the following command:

`docker logs [-f] <container_name>`

### Volumes
***/mnt***  
The volume mounted to '/mnt' is the scanned directory. It is set by the *volume* local directory value in the **docker-compose.yaml** file. Ensure that the volume is updated before starting the container. The container will terminate right after the scan, if it will not have any transcoding to perform.

The mounted volume will be scanned recursively. This can be used to specify the depth of video trancoding. For example, Plex TV series have a folder structure of the root directory, the show name, then the season folder, which contain the respective episodes.

* TV Shows
  * Random Show
    * Season 01
    * Season 02
    * Season 03
  * Some Other Show
    * Season 01
    * Season 02

Mounting 'Random Show' will scan all of its season directories for video files to transcode. However, mounting a specific season will only scan that directory for video files that need to be transcoded to h.265 HVC1 MP4. If the root folder containing all of the TV shows is mounted, it will scan all of the TV shows and respective seasons for videos to transcode.

Movies are typically one flat directory. Mounting the directory will scan and process all video files. This is when setting the **BATCH** environment variable can help ensure the transcoding is not running for days.

***CAVEATS***  
**OPTIONAL: Mounting */tmp* volume**  
SQLite: as persistent data means the SQLite database file needs to be deleted, or the table cleared. This is most notably going to be an issue when the */mnt* volume is changed, and the paths and filenames are no longer valid.

Logging: Ideally, this is for troubleshooting purposes. The file will continue to grow, with new entries appending to the existing file.

### Known Error
***returned non-zero exit status 243***  
When setting the user's UID and GID in the *docker-compose.yaml* file or running a container manually, if it is not a valid UID on the host, the `subprocess.run()` execution will create exceptions, and the exit status 243.
