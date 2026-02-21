import os
import re
import subprocess
import shutil

POSTGRES_USER = "erp_user"
POSTGRES_PASSWORD = "powertek123"
DATABASE_NAME = "erp_db"
BUCKET_NAME = "erp-databackup"
GCS_FILE = "" # Leave empty to automatically find the latest backup
TEMP_DIR = "/tmp/erp_restore"
FILESTORE_DIR = "/opt/odoo/filestore"
ODOO_USER = "odoo"

os.makedirs(TEMP_DIR, exist_ok=True)
os.environ["PGPASSWORD"] = POSTGRES_PASSWORD

# Find latest backup if GCS_FILE is not specific
if not GCS_FILE:
    print("No specific backup file provided. Finding the latest backup...")
    try:
        ls_cmd = f"gsutil ls gs://{BUCKET_NAME}/erp_backups/*.dump"
        result = subprocess.run(ls_cmd, shell=True, check=True, capture_output=True, text=True)
        backups = result.stdout.strip().split('\n')
        if not backups:
            print("No backups found in bucket.")
            exit(1)
        # Sort and get the latest
        GCS_FILE_PATH = sorted(backups)[-1]
        print(f"Latest backup identified: {GCS_FILE_PATH}")
    except subprocess.CalledProcessError:
        print("Error listing backups in GCS.")
        exit(1)
else:
    GCS_FILE_PATH = f"gs://{BUCKET_NAME}/{GCS_FILE}"

LOCAL_FILE = os.path.join(TEMP_DIR, os.path.basename(GCS_FILE_PATH))

# Download backup
print(f"Downloading backup from {GCS_FILE_PATH}...")
download_cmd = f'gsutil cp "{GCS_FILE_PATH}" "{LOCAL_FILE}"'
try:
    subprocess.run(download_cmd, check=True, shell=True)
    print(f"Backup downloaded successfully: {LOCAL_FILE}")
except subprocess.CalledProcessError as e:
    print(f"Download failed. Error: {e}")
    exit(1)

# Terminate active connections to the database
print(f"Terminating active connections to '{DATABASE_NAME}'...")
terminate_cmd = f"sudo -u postgres psql -d postgres -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{DATABASE_NAME}' AND pid <> pg_backend_pid();\""
try:
    subprocess.run(terminate_cmd, shell=True, check=True, capture_output=True)
    print("Active connections terminated.")
except subprocess.CalledProcessError as e:
    print(f"Warning: Could not terminate connections.")

# Drop existing database (as postgres superuser)
print(f"Dropping existing database '{DATABASE_NAME}'...")
drop_cmd = f"sudo -u postgres psql -d postgres -c 'DROP DATABASE IF EXISTS {DATABASE_NAME};'"
try:
    subprocess.run(drop_cmd, shell=True, check=True, capture_output=True)
    print("Database dropped successfully.")
except subprocess.CalledProcessError as e:
    print(f"Warning: Could not drop database.")
    exit(1)

# Create fresh database (as postgres superuser)
print(f"Creating fresh database '{DATABASE_NAME}'...")
create_cmd = f"sudo -u postgres psql -d postgres -c 'CREATE DATABASE {DATABASE_NAME} OWNER {POSTGRES_USER};'"
try:
    subprocess.run(create_cmd, shell=True, check=True, capture_output=True)
    print("Database created successfully.")
except subprocess.CalledProcessError as e:
    print(f"Create failed.")
    exit(1)

# Restore without --clean flag
print(f"Restoring database '{DATABASE_NAME}' from: {LOCAL_FILE}...")
restore_cmd = ["pg_restore", "-U", POSTGRES_USER, "-h", "localhost", "-d", DATABASE_NAME, "-v", "--no-owner", "--no-acl", LOCAL_FILE]

try:
    restore_process = subprocess.run(restore_cmd, check=False, text=True, capture_output=True)
    if restore_process.returncode == 0:
        print("Database restored successfully!")
    else:
        # pg_restore often returns non-zero even on success due to warnings
        print("Restore completed with warnings (this is often normal):")
        if restore_process.stderr:
            print(restore_process.stderr[:500])  # Print first 500 chars
except Exception as e:
    print(f"Restore error: {e}")
    exit(1)

os.remove(LOCAL_FILE)
print(f"Temporary backup file removed: {LOCAL_FILE}")

dump_basename = os.path.basename(GCS_FILE_PATH)
timestamp_match = re.search(r"erp_backup_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})\.dump", dump_basename)

if timestamp_match:
    timestamp = timestamp_match.group(1)
    filestore_archive_name = f"erp_filestore_{timestamp}.tar.gz"
    filestore_gcs_path = f"gs://{BUCKET_NAME}/erp_backups/{filestore_archive_name}"
    filestore_local_path = os.path.join(TEMP_DIR, filestore_archive_name)

    print(f"Looking for filestore archive: {filestore_gcs_path}")

    check_cmd = f'gsutil ls "{filestore_gcs_path}"'
    check_result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)

    if check_result.returncode == 0:
        print(f"Downloading filestore archive...")
        try:
            subprocess.run(f'gsutil cp "{filestore_gcs_path}" "{filestore_local_path}"', shell=True, check=True)
            print("Filestore archive downloaded.")

            if os.path.isdir(FILESTORE_DIR):
                print(f"Clearing existing filestore at {FILESTORE_DIR}...")
                shutil.rmtree(FILESTORE_DIR)

            os.makedirs(FILESTORE_DIR, exist_ok=True)

            print(f"Extracting filestore archive...")
            subprocess.run(
                ["tar", "-xzf", filestore_local_path, "-C", os.path.dirname(FILESTORE_DIR)],
                check=True
            )
            subprocess.run(["chown", "-R", f"{ODOO_USER}:{ODOO_USER}", FILESTORE_DIR], check=True)
            print("Filestore restored and ownership fixed.")

            os.remove(filestore_local_path)
            print("Filestore archive cleaned up.")
        except subprocess.CalledProcessError as e:
            print(f"WARNING: Filestore restore failed: {e}")
            print("Database was restored successfully, but attachments may be missing.")
    else:
        print(f"No filestore archive found for this backup (older backup without filestore).")
        print("Database restored, but file attachments may be missing.")
else:
    print("Could not extract timestamp from backup filename. Skipping filestore restore.")

print("\nRestore process complete!")
