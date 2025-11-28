#!/bin/bash

# Activate the Python virtual environment
source $HOME/odoo-build/venv/bin/activate

# Define variables
ODOO_BIN="$HOME/odoo-build/odoo/odoo-bin"
CONFIG_FILE="$HOME/odoo.conf"
LOG_FILE="$HOME/odoo-logs/sysout.log"
DATABASE="odoo_db"

# Help function
function show_help {
    echo "Usage: $0 [--reinit]"
    echo "  --reinit : Start Odoo with database reinitialization (includes -i base)"
    echo "  If no parameter is provided, Odoo starts without reinitializing the database."
}

# Parse input argument
REINIT=false
if [ "$1" == "--reinit" ]; then
    REINIT=true
elif [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    show_help
    exit 0
elif [ -n "$1" ]; then
    echo "Invalid argument: $1"
    show_help
    exit 1
fi

# Stop any existing Odoo instance
echo "Stopping existing Odoo instance (if any)..."
PID=$(ps aux | grep "$ODOO_BIN" | grep -v grep | awk '{print $2}')
if [ ! -z "$PID" ]; then
    kill "$PID"
    echo "Stopped Odoo process with PID: $PID"
else
    echo "No existing Odoo instance found."
fi

# Start Odoo based on the selected mode
if [ "$REINIT" = true ]; then
    echo "Starting Odoo with database reinitialization..."
    nohup python3 "$ODOO_BIN" -d "$DATABASE" -i base --config="$CONFIG_FILE" &> "$LOG_FILE" &
else
    echo "Starting Odoo without database reinitialization..."
    nohup python3 "$ODOO_BIN" --config="$CONFIG_FILE" &> "$LOG_FILE" &
fi

NEW_PID=$!

# Confirm that Odoo has started
if [ $? -eq 0 ]; then
    echo "Odoo started successfully with PID: $NEW_PID"
    echo "Logs can be found at: $LOG_FILE"
else
    echo "Failed to start Odoo. Check the logs at: $LOG_FILE"
fi
