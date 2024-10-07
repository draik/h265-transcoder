FROM python:3.12-alpine3.20

RUN apk update && \
    apk upgrade && \
    apk add exiftool ffmpeg mkvtoolnix sqlite x265 x265-libs && \
    pip install python-ffmpeg

COPY ./h265_transcoder /app/h265_transcoder

ARG UNAME="h265usr"

ARG GNAME="h265grp"

ARG UID=1000

ARG GID=1000

RUN addgroup -g ${GID} ${GNAME} && \
    adduser -D -H -u ${UID} -G ${GNAME} ${UNAME}

USER ${UNAME}

WORKDIR /app

ENV BATCH=0

ENV DEBUG="False"

ENV DELETE="False"

ENV PERSIST="False"

ENV RETRY_FAILED="False"

ENV TRANSCODE="True"

ENV TZ="UTC"

CMD ["/usr/local/bin/python", "-m", "h265_transcoder"]