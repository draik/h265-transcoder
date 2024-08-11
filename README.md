# H.265 Converter

## Description
Scan a directory for video files that need to be converted to h.265 HVC1 MP4 format, and process the findings. These are possible scan results:

* MKV (convert) - All MKV will be converted to MP4 even if it's h.265 HVC1
* MP4 (convert) - Convert MP4 if not h.265 HVC1
* MP4 (skipped) - MP4 is already h.265 HVC1

***CAVEAT*** - the conversion is for **ONE** video stream (track 0) and **ONE** audio stream (track 1). If the file has multiple audio tracks (i.e.: anime dubs), it may choose the wrong language, as there is no standard for ordering tracks. Furthermore, as this will only use those two tracks, all others will be ignored, such as subtitles. Extract any subtitles with `mkvextract` prior to conversion as original files are removed after a successful conversion.

## How It Works
Once the container starts, it scans the mounted volume for video files to convert and update metadata. If no files are found, the container will shut itself down. The found files will be inserted into the SQLite database, and queued for processing. After scans are complete, the conversion will begin for files with *convert* set to "Y" until the queue is complete. Conversion results will be *failed* or *done*. Failed conversions will be processed again after the *convert* batch is complete.  

After a completed conversion queue, all files will have the *Title* metadata updated to match the filename (without extension), and the *Comment* tag removed.

## Docker

### Build Image
Build the docker image using the following command:

`docker build -t draikx21/h265_converter .`

### Run a Container
The container will need a mounted volume to "/mnt" which contains video files to convert, or it will terminate immediately.

`docker run -v /path/to/videos:/mnt draikx21/h265_coverter`

### Environment Variables

***BATCH*** (default = 0) is for the amount of video files to convert. The default value is "0" (zero) which is unlimited, and will go through all of the video files it found in the scan. The list depends on the result order from the `os.walk` scan, as the limit is for the top batch count.

:exclamation: Be mindful of the resource usage, and overworking the machine for long periods of video conversions.

***CONVERT*** (default = "True") will begin a conversion task. If set to a "False" value, it will only scan the files, and update the metadata on MP4 files. 

***DEBUG*** (default = "False") pertains to the log file. It will log all INFO-level and higher messages. For more verbosity, setting the value to "True" will enable DEBUG-level logging. 

### Reading the Docker Logs
The console output is setup with DEBUG-level logging. While the Docker container is running, the console will display the current actions, but all console output is available in the Docker logs, even after it shuts down (and container is not removed). Read the Docker logs with the following command:

`docker logs <image_name>`

### Volumes
The mount to '/mnt' is the scanned directory. It is set by the *volume* local directory value in the **docker-compose.yaml** file. Ensure that the volume is updated before starting the container. The container will terminate right after the scan, if it will not have any conversions to perform.

The mounted volume will be scanned recursively. This can be used to specify the depth of video conversions. For example, Plex TV series have a folder structure of the root directory, the show name, then the season folder, which contain the respective episodes.

* TV Shows
  * Random Show
    * Season 01
    * Season 02
    * Season 03
  * Some Other Show
    * Season 01
    * Season 02

Mounting 'Random Show' will scan all of its season directories for video files to convert. However, mounting a specific season will only scan that directory for video files that need to be converted to h.265 HVC1 MP4. If the root folder containing all of the TV shows is mounted, it will scan all of the TV shows and respective seasons for videos to convert.

Movies are typically one flat directory. Mounting the directory will scan and process all video files. This is when setting the **BATCH** environment variable can help ensure the conversions are not running for days.
