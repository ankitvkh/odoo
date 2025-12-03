import os
import datetime

POSTGRES_USER = "odoo_user_new"
POSTGRES_PASSWORD = "odoo123"
DATABASE_NAME = "odoo_new"
BUCKET_NAME = "your-gcs-bucket-name"  # Replace with gcp bucket name
TEMP_DIR = "/tmp/odoo_backup"

os.makedirs(TEMP_DIR, exist_ok=True)

TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
DUMP_PATH = os.path.join(TEMP_DIR, f"odoo_backup_{TIMESTAMP}.dump")

os.environ["PGPASSWORD"] = POSTGRES_PASSWORD

print("Creating DB backup...")
if os.system(f'pg_dump -U {POSTGRES_USER} -h localhost -F c -b -v -f "{DUMP_PATH}" {DATABASE_NAME}') != 0:
    print("Backup failed.")
    exit(1)

print("Uploading to GCS...")
if os.system(f'gsutil cp "{DUMP_PATH}" gs://{BUCKET_NAME}/odoo_backups/') != 0:
    print("Upload failed.")
    exit(1)

print("Backup complete. Cleaning up...")
os.remove(DUMP_PATH)
