#!/bin/bash

# Path to the Odoo directory
ODOO_DIR="/Users/rohitkumar/IdeaProjects/odoo"
PYTHON_BIN="$ODOO_DIR/.venv/bin/python"
ODOO_BIN="$ODOO_DIR/odoo-bin"
CONFIG_FILE="$ODOO_DIR/odoo.conf"
LOG_FILE="$ODOO_DIR/odoo.log"

echo "Starting Odoo server..."

# Navigate to Odoo directory
cd "$ODOO_DIR"

# Run Odoo in the background
nohup "$PYTHON_BIN" "$ODOO_BIN" -c "$CONFIG_FILE" > "$LOG_FILE" 2>&1 &

ODOO_PID=$!

echo "Odoo server started with PID: $ODOO_PID"
echo "Logs are being written to: $LOG_FILE"
echo "Checking if port 8069 is listening..."

# Wait a bit for startup
sleep 5

if lsof -i :8069 > /dev/null; then
    echo "Odoo is listening on port 8069!"
else
    echo "Warning: Port 8069 is not yet listening. Check $LOG_FILE for details."
fi
