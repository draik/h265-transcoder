FROM python:3.12-alpine3.20

RUN apk update && \
    apk add exiftool ffmpeg mkvtoolnix sqlite x265 x265-libs

COPY ./h265_converter /app/h265_converter

ARG UNAME="convusr"

ARG GNAME="convgrp"

ARG UID=1000

ARG GID=1000

RUN addgroup -g ${GID} ${GNAME} && \
    adduser -D -H -u ${UID} -G ${GNAME} ${UNAME}

USER ${UNAME}

WORKDIR /app

ENV BATCH=0

ENV CONVERT="True"

ENV DEBUG="False"

ENV DELETE="False"

ENV RETRY_FAILED="False"

ENV TZ="UTC"

CMD ["/usr/local/bin/python", "-m", "h265_converter"]