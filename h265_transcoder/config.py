import tempfile

temp_dir = tempfile.TemporaryDirectory(prefix="transcode-")
log_filename = "transcode.log"
schema_file = "/app/h265_transcoder/schema.sql"
persist_db = "/tmp/transcode.db"
temp_db = "transcode.db"
