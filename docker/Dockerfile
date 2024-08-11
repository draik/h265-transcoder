FROM python:3.12-slim

RUN apt update && \
    apt install -y exiftool \
                    ffmpeg \
                    libx265-199 \
                    mkvtoolnix \
                    x265

COPY ./h265_converter /app

WORKDIR /app

ENV BATCH=0

ENV DEBUG="False"

CMD ["/usr/local/bin/python", "/app"]