#!/bin/bash

# Activate the Python virtual environment
source $HOME/odoo-build/venv/bin/activate

# Define variables
ODOO_BIN="$HOME/odoo-build/odoo/odoo-bin"
CONFIG_FILE="$HOME/odoo.conf"
LOG_FILE="$HOME/odoo-logs/sysout.log"
DATABASE="odoo_db"

# Stop any existing Odoo instance
echo "Stopping existing Odoo instance (if any)..."
PID=$(ps aux | grep "$ODOO_BIN" | grep -v grep | awk '{print $2}')
if [ ! -z "$PID" ]; then
    kill "$PID"
    echo "Stopped Odoo process with PID: $PID"
else
    echo "No existing Odoo instance found."
fi

# Start Odoo without reinitializing the database
echo "Starting Odoo..."
nohup python3 "$ODOO_BIN" --config="$CONFIG_FILE" &> "$LOG_FILE" &
NEW_PID=$!

# Confirm that Odoo has started
if [ $? -eq 0 ]; then
    echo "Odoo started successfully with PID: $NEW_PID"
    echo "Logs can be found at: $LOG_FILE"
else
    echo "Failed to start Odoo. Check the logs at: $LOG_FILE"
fi
