import os
import datetime

POSTGRES_USER = "erp_user"
POSTGRES_PASSWORD = "powertek123"
DATABASE_NAME = "erp_db"
BUCKET_NAME = "erp-databackup"  # Replace with gcp bucket name
TEMP_DIR = "/tmp/erp_backup"

os.makedirs(TEMP_DIR, exist_ok=True)

TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
DUMP_PATH = os.path.join(TEMP_DIR, f"erp_backup_{TIMESTAMP}.dump")

os.environ["PGPASSWORD"] = POSTGRES_PASSWORD

print("Creating DB backup...")
if os.system(f'pg_dump -U {POSTGRES_USER} -h localhost -F c -b -v -f "{DUMP_PATH}" {DATABASE_NAME}') != 0:
    print("Backup failed.")
    exit(1)

print("Uploading to GCS...")
if os.system(f'gsutil cp "{DUMP_PATH}" gs://{BUCKET_NAME}/erp_backups/') != 0:
    print("Upload failed.")
    exit(1)

print("Backup complete. Cleaning up...")
os.remove(DUMP_PATH)
