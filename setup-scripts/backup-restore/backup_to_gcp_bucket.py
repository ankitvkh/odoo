import os
import re
import datetime
import subprocess
import shutil

RETENTION_DAYS = 7

POSTGRES_USER = "erp_user"
POSTGRES_PASSWORD = "powertek123"
DATABASE_NAME = "erp_db"
BUCKET_NAME = "erp-databackup"  # Replace with gcp bucket name
TEMP_DIR = "/tmp/erp_backup"
FILESTORE_DIR = "/opt/odoo/filestore"

os.makedirs(TEMP_DIR, exist_ok=True)

TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
DUMP_PATH = os.path.join(TEMP_DIR, f"erp_backup_{TIMESTAMP}.dump")
FILESTORE_ARCHIVE_NAME = f"erp_filestore_{TIMESTAMP}.tar.gz"
FILESTORE_ARCHIVE_PATH = os.path.join(TEMP_DIR, FILESTORE_ARCHIVE_NAME)

os.environ["PGPASSWORD"] = POSTGRES_PASSWORD

print("Creating DB backup...")
if os.system(f'pg_dump -U {POSTGRES_USER} -h localhost -F c -b -v -f "{DUMP_PATH}" {DATABASE_NAME}') != 0:
    print("DB backup failed.")
    exit(1)

print("Uploading DB backup to GCS...")
if os.system(f'gsutil cp "{DUMP_PATH}" gs://{BUCKET_NAME}/erp_backups/') != 0:
    print("DB upload failed.")
    exit(1)

print("DB backup uploaded. Cleaning up dump file...")
os.remove(DUMP_PATH)

if os.path.isdir(FILESTORE_DIR) and os.listdir(FILESTORE_DIR):
    print(f"Creating filestore archive from {FILESTORE_DIR}...")
    try:
        subprocess.run(
            ["tar", "-czf", FILESTORE_ARCHIVE_PATH, "-C", os.path.dirname(FILESTORE_DIR), os.path.basename(FILESTORE_DIR)],
            check=True
        )
        print("Uploading filestore archive to GCS...")
        if os.system(f'gsutil cp "{FILESTORE_ARCHIVE_PATH}" gs://{BUCKET_NAME}/erp_backups/') != 0:
            print("Filestore upload failed.")
            exit(1)
        print("Filestore archive uploaded. Cleaning up...")
        os.remove(FILESTORE_ARCHIVE_PATH)
    except subprocess.CalledProcessError as e:
        print(f"Filestore archive creation failed: {e}")
        exit(1)
else:
    print(f"Filestore directory {FILESTORE_DIR} is empty or does not exist. Skipping filestore backup.")

print("Backup complete!")

print(f"\nCleaning up backups older than {RETENTION_DAYS} days...")
cutoff_date = datetime.datetime.now() - datetime.timedelta(days=RETENTION_DAYS)

try:
    ls_result = subprocess.run(
        f"gsutil ls gs://{BUCKET_NAME}/erp_backups/",
        shell=True, check=True, capture_output=True, text=True
    )
    all_files = [f.strip() for f in ls_result.stdout.strip().split('\n') if f.strip()]

    deleted_count = 0
    for gcs_path in all_files:
        basename = os.path.basename(gcs_path)
        match = re.search(r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})", basename)
        if match:
            try:
                file_date = datetime.datetime.strptime(match.group(1), "%Y-%m-%d_%H-%M-%S")
                if file_date < cutoff_date:
                    print(f"  Deleting old backup: {basename}")
                    subprocess.run(f'gsutil rm "{gcs_path}"', shell=True, check=True)
                    deleted_count += 1
            except ValueError:
                continue

    if deleted_count > 0:
        print(f"Cleaned up {deleted_count} old backup file(s).")
    else:
        print("No old backups to clean up.")
except subprocess.CalledProcessError as e:
    print(f"Warning: Cleanup failed: {e}. Backups were saved successfully.")
