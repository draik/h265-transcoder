import tempfile

temp_dir = tempfile.TemporaryDirectory(prefix="convert-")
log_filename = "convert.log"
schema_file = "/app/h265_converter/schema.sql"
persist_db = "/tmp/convert.db"
temp_db = "convert.db"
