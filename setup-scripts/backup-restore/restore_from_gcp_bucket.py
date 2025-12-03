import os
import subprocess

POSTGRES_USER = "odoo_user"
POSTGRES_PASSWORD = "odoo123"
DATABASE_NAME = "odoo_db"
BUCKET_NAME = "odoo-backup-store"
GCS_FILE = "odoo_backups/odoo_backup_2025-11-25_10-33-41.dump"
TEMP_DIR = "/tmp/odoo_restore"

os.makedirs(TEMP_DIR, exist_ok=True)
os.environ["PGPASSWORD"] = POSTGRES_PASSWORD

LOCAL_FILE = os.path.join(TEMP_DIR, os.path.basename(GCS_FILE))

# Download backup
print("Downloading backup from GCS...")
download_cmd = f'gsutil cp gs://{BUCKET_NAME}/{GCS_FILE} "{LOCAL_FILE}"'
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

# Cleanup
os.remove(LOCAL_FILE)
print(f"Temporary backup file removed: {LOCAL_FILE}")
print("\nRestore process complete!")
