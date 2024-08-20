FROM python:3.12-alpine3.20

RUN apk update && \
    apk add exiftool ffmpeg mkvtoolnix x265 x265-libs

COPY ./h265_converter /app/h265_converter

WORKDIR /app

ENV BATCH=0

ENV DEBUG="False"

ENV DELETE="False"

ENV TZ="UTC"

CMD ["/usr/local/bin/python", "-m", "h265_converter"]