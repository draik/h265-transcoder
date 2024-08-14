FROM python:3.12-slim

RUN apt update && \
    apt install -y exiftool \
                    ffmpeg \
                    libx265-199 \
                    mkvtoolnix \
                    x265

COPY ./h265_converter /app/h265_converter

WORKDIR /app

ENV BATCH=0

ENV DEBUG="False"

ENV DELETE="False"

CMD ["/usr/local/bin/python", "-m", "h265_converter"]