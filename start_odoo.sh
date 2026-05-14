#!/bin/bash

# Kill any existing Odoo process on port 8069
lsof -ti:8069 | xargs kill -9 2>/dev/null

# Default parameters
DB_NAME=${1:-odoo_db}
DB_HOST="localhost"
DB_USER="rohitkumar"
PORT=8069

echo "Starting Odoo on port $PORT with database $DB_NAME..."

# Start Odoo using the virtual environment
./.venv/bin/python3 odoo-bin \
    --config=odoo.conf \
    --database=$DB_NAME \
    --db_host=$DB_HOST \
    --db_user=$DB_USER \
    --http-port=$PORT \
    "${@:2}"
