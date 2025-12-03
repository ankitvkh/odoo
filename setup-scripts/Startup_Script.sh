#!/bin/bash

ODOO_VERSION="18.0"
PYTHON_VERSION="3"
NODEJS_VERSION="18"

PROJECT_ID="verdant-algebra-475509-c6"
DB_NAME="odoo_db"
POSTGRES_USER="odoo_user"
POSTGRES_PASSWORD="odoo123"

ODOO_USER="odoo"
WORK_DIR="/opt/odoo"
GITHUB_REPO="https://github.com/ankitvkh/odoo.git"
GITHUB_BRANCH="Anish-Kumar-09-patch-1"

ADMIN_EMAIL="admin"
ADMIN_PASSWORD="admin"

VENV_DIR="${WORK_DIR}/venv"
ADDONS_DIR="${WORK_DIR}/custom_addons"
ODOO_DIR="${WORK_DIR}/odoo"
CONFIG_FILE="${WORK_DIR}/odoo.conf"
LOG_DIR="/var/log/odoo"
LOG_FILE="${LOG_DIR}/odoo.log"
SERVICE_FILE="/etc/systemd/system/odoo.service"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $1" >> /var/log/startup-script.log
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [SUCCESS] $1" >> /var/log/startup-script.log
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [WARNING] $1" >> /var/log/startup-script.log
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $1" >> /var/log/startup-script.log
}

set -e

error_handler() {
    local line_no=$1
    local bash_lineno=$2
    local last_command=$3
    local code=$4
    
    log_error "Script failed at line $line_no (bash line $bash_lineno): Command '$last_command' exited with status $code"
    
    if [[ "$last_command" =~ (certbot|npm|lessc|wkhtmltopdf) ]]; then
        log_warning "Non-critical command failed, continuing installation..."
        return 0
    fi
    
    exit $code
}

trap 'error_handler ${LINENO} $BASH_LINENO "$BASH_COMMAND" $?' ERR

if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root (use sudo)"
   exit 1
fi

get_vm_info() {
    EXTERNAL_IP=""
    DOMAIN_NAME=""
    
    if command -v curl >/dev/null 2>&1; then
        EXTERNAL_IP=$(curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip 2>/dev/null || echo "")
    fi
    
    if [[ -z "$EXTERNAL_IP" ]] && command -v curl >/dev/null 2>&1; then
        EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null || echo "")
    fi
    
    if [[ -z "$EXTERNAL_IP" ]]; then
        log_warning "Could not determine external IP address, using placeholder"
        EXTERNAL_IP="YOUR_VM_IP"
    fi
    
    echo "$EXTERNAL_IP|$DOMAIN_NAME"
}

VM_INFO=$(get_vm_info)
EXTERNAL_IP=$(echo $VM_INFO | cut -d'|' -f1)
DOMAIN_NAME=$(echo $VM_INFO | cut -d'|' -f2)

log_info "Detected external IP: $EXTERNAL_IP"
if [[ -n "$DOMAIN_NAME" ]]; then
    log_info "Detected domain name: $DOMAIN_NAME"
    SERVER_NAME="$DOMAIN_NAME"
else
    SERVER_NAME="$EXTERNAL_IP"
fi

log_info "Using local PostgreSQL instance inside VM"
DB_HOST="127.0.0.1"
log_info "DB host set to ${DB_HOST}"



log_info "Cleaning up any existing processes..."
systemctl stop odoo 2>/dev/null || true
pkill -f "odoo-bin" 2>/dev/null || true
fuser -k 8069/tcp 2>/dev/null || true
sleep 3

log_info "Step 1: Creating system user ${ODOO_USER}..."
if ! id "${ODOO_USER}" &>/dev/null; then
    useradd -m -d /home/${ODOO_USER} -s /bin/bash ${ODOO_USER}
    log_success "User ${ODOO_USER} created successfully"
else
    log_info "User ${ODOO_USER} already exists"
fi

log_info "Step 2: Updating system packages..."
export DEBIAN_FRONTEND=noninteractive
apt-get update && apt-get upgrade -y

log_info "Step 3: Installing all system dependencies..."
ALL_PACKAGES="wget curl git vim nano unzip ca-certificates gnupg software-properties-common \
python3 python3-dev python3-pip python3-venv build-essential pkg-config \
postgresql postgresql-client libpq-dev \
libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libssl-dev libffi-dev \
libtiff5-dev libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev \
libxcb1-dev libevent-dev fontconfig xfonts-75dpi xfonts-base \
nginx"

log_info "Installing packages (this may take several minutes)..."
if apt-get install -y $ALL_PACKAGES; then
    log_success "All system packages installed successfully"
else
    log_warning "Some packages failed to install, retrying with update..."
    apt-get update
    apt-get install -y $ALL_PACKAGES || {
        log_error "Critical packages failed to install"
        exit 1
    }
fi

log_success "Core system dependencies installed successfully"
log_info "Step 4: Ensure PostgreSQL is running and DB/user exist locally"

# Start and enable PostgreSQL service
if systemctl is-active --quiet postgresql; then
    log_info "PostgreSQL already running"
else
    log_info "Starting PostgreSQL service..."
    systemctl enable --now postgresql
    sleep 3
fi

# Create database user if it doesn't exist
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='${POSTGRES_USER}'" | grep -q 1; then
    log_info "Creating Postgres user ${POSTGRES_USER}..."
    sudo -u postgres psql -c "CREATE USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';"
    log_success "User ${POSTGRES_USER} created"
else
    log_info "Postgres user ${POSTGRES_USER} already exists"
fi

# Create database if it doesn't exist
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'" | grep -q 1; then
    log_info "Creating database ${DB_NAME}..."
    sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME} OWNER ${POSTGRES_USER};"
    log_success "Database ${DB_NAME} created"
else
    log_info "Database ${DB_NAME} already exists"
fi

connection_success=false
for i in {1..10}; do
    if PGPASSWORD=${POSTGRES_PASSWORD} psql -h ${DB_HOST} -U ${POSTGRES_USER} -d ${DB_NAME} -c 'SELECT version()' >/dev/null 2>&1; then
        log_success "Local Postgres connection successful"
        connection_success=true
        break
    else
        log_warning "Connection attempt $i/10 failed, retrying in 10 seconds..."
        sleep 10
    fi
done

if [[ "$connection_success" != "true" ]]; then
    log_error "Failed to connect to local Postgres after 10 attempts"
    log_error "Please verify:"
    log_error "  1. Postgres service is running"
    log_error "  2. Local firewall (ufw) allows connections or Odoo will connect over localhost"
    log_error "  3. Database credentials are correct"
    exit 1
fi

log_info "Step 5: Installing Node.js..."
set +e
if ! command -v node >/dev/null 2>&1; then
    log_info "Installing Node.js from NodeSource repository..."
    if curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg; then
        echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODEJS_VERSION}.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list
        apt-get update
        if apt-get install -y nodejs; then
            log_success "Node.js installed successfully"
        else
            log_warning "NodeSource installation failed, trying Ubuntu repository..."
            apt-get install -y nodejs npm || log_warning "Node.js installation failed, continuing without it"
        fi
    else
        log_warning "Failed to add NodeSource repository, trying Ubuntu packages..."
        apt-get install -y nodejs npm || log_warning "Node.js installation failed completely"
    fi
else
    log_info "Node.js already installed"
fi

if command -v npm >/dev/null 2>&1; then
    if ! command -v lessc >/dev/null 2>&1; then
        log_info "Installing Less compiler..."
        npm install -g less less-plugin-clean-css || {
            log_warning "npm Less installation failed, trying apt..."
            apt-get install -y node-less || log_warning "Less installation failed, Odoo will still work"
        }
    fi
fi
set -e

log_info "Step 6: Installing wkhtmltopdf..."
set +e
if ! command -v wkhtmltopdf >/dev/null 2>&1; then
    if apt-get install -y wkhtmltopdf; then
        log_success "wkhtmltopdf installed from repository"
    else
        log_warning "Repository installation failed, trying manual download..."
        if wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.jammy_amd64.deb -O /tmp/wkhtmltox.deb; then
            if dpkg -i /tmp/wkhtmltox.deb; then
                log_success "wkhtmltopdf installed manually"
            else
                apt-get install -f -y || true
                log_warning "wkhtmltopdf installation had issues, PDF generation may be limited"
            fi
            rm -f /tmp/wkhtmltox.deb
        else
            log_warning "wkhtmltopdf installation failed, PDF generation will be limited"
        fi
    fi
else
    log_info "wkhtmltopdf already installed"
fi
set -e

log_info "Step 7: Setting up working directory structure..."
mkdir -p ${WORK_DIR} ${LOG_DIR}
chown -R ${ODOO_USER}:${ODOO_USER} ${WORK_DIR} ${LOG_DIR}

log_info "Step 8: Cloning Odoo repository..."
if [[ -d "${ODOO_DIR}" ]] && [[ -f "${ODOO_DIR}/odoo-bin" ]]; then
    log_info "Odoo repository exists, updating..."
    sudo -u ${ODOO_USER} bash -c "cd ${ODOO_DIR} && git pull origin ${GITHUB_BRANCH}" || {
        log_warning "Git pull failed, re-cloning..."
        rm -rf ${ODOO_DIR}
        sudo -u ${ODOO_USER} git clone -b ${GITHUB_BRANCH} ${GITHUB_REPO} ${ODOO_DIR}
    }
else
    log_info "Cloning Odoo repository from ${GITHUB_REPO}..."
    sudo -u ${ODOO_USER} git clone -b ${GITHUB_BRANCH} ${GITHUB_REPO} ${ODOO_DIR}
fi

if [[ ! -f "${ODOO_DIR}/odoo-bin" ]]; then
    log_error "odoo-bin not found in ${ODOO_DIR}"
    log_error "Please ensure your repository contains the odoo-bin executable"
    exit 1
fi

log_success "Odoo repository ready"

log_info "Step 9: Creating Python virtual environment..."
if [[ ! -d "${VENV_DIR}" ]]; then
    sudo -u ${ODOO_USER} python3 -m venv ${VENV_DIR}
fi

log_info "Step 10: Installing Python dependencies..."
sudo -u ${ODOO_USER} ${VENV_DIR}/bin/pip install --upgrade pip wheel setuptools

if [[ -f "${ODOO_DIR}/requirements.txt" ]]; then
    log_info "Installing from repository requirements.txt..."
    sudo -u ${ODOO_USER} ${VENV_DIR}/bin/pip install -r ${ODOO_DIR}/requirements.txt || {
        log_warning "Requirements.txt installation failed, installing essential packages manually..."
        sudo -u ${ODOO_USER} ${VENV_DIR}/bin/pip install psycopg2-binary lxml Pillow python-dateutil pytz
    }
else
    log_info "Installing essential Odoo dependencies..."
    sudo -u ${ODOO_USER} ${VENV_DIR}/bin/pip install \
        psycopg2-binary lxml Pillow python-dateutil pytz polib \
        reportlab requests passlib docutils babel decorator || {
        log_error "Failed to install essential Python packages"
        exit 1
    }
fi

log_success "Python dependencies installed"

log_info "Step 11: Setting up custom addons..."
sudo -u ${ODOO_USER} mkdir -p ${ADDONS_DIR}
if [[ -d "${ODOO_DIR}/addons" ]]; then
    sudo -u ${ODOO_USER} cp -r ${ODOO_DIR}/addons/* ${ADDONS_DIR}/ 2>/dev/null || true
fi

log_info "Step 12: Creating Odoo configuration..."
sudo -u ${ODOO_USER} cat > ${CONFIG_FILE} << EOF
[options]
db_host = ${DB_HOST}
db_port = 5432
db_user = ${POSTGRES_USER}
db_password = ${POSTGRES_PASSWORD}

addons_path = ${ODOO_DIR}/addons,${ADDONS_DIR}
data_dir = ${WORK_DIR}/filestore
logfile = ${LOG_FILE}

xmlrpc_interface = 0.0.0.0
xmlrpc_port = 8069
proxy_mode = False
web.base.url = http://${SERVER_NAME}:8069

admin_passwd = admin

workers = 0
max_cron_threads = 1
limit_time_cpu = 600
limit_time_real = 1200

server_wide_modules = base,web
without_demo = True
db_template = template0
list_db = False
db_name = ${DB_NAME}
EOF

chown ${ODOO_USER}:${ODOO_USER} ${CONFIG_FILE}
sudo -u ${ODOO_USER} mkdir -p ${WORK_DIR}/filestore

log_info "Step 13: Testing Odoo configuration..."
if sudo -u ${ODOO_USER} timeout 30s ${VENV_DIR}/bin/python ${ODOO_DIR}/odoo-bin -c ${CONFIG_FILE} --stop-after-init; then
    log_success "Odoo configuration test passed"
else
    log_error "Odoo configuration test failed"
    exit 1
fi

log_info "Step 14: Creating Odoo systemd service..."
cat > ${SERVICE_FILE} << EOF
[Unit]
Description=Odoo
After=network.target

[Service]
User=${ODOO_USER}
Group=${ODOO_USER}
ExecStart=${VENV_DIR}/bin/python3 ${ODOO_DIR}/odoo-bin --config=${CONFIG_FILE}
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

log_info "Step 15: Configuring Nginx..."
cat > /etc/nginx/sites-available/odoo << EOF
upstream odoo {
    server 127.0.0.1:8069;
}

server {
    listen 80;
    server_name ${SERVER_NAME};

    location / {
        proxy_pass http://odoo;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-Port \$server_port;
        proxy_buffering off;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /websocket {
        proxy_pass http://odoo;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

if nginx -t; then
    systemctl restart nginx
    systemctl enable nginx
    log_success "Nginx configured and started"
else
    log_error "Nginx configuration test failed"
    exit 1
fi

log_info "Step 16: Initializing Cloud SQL database..."

# First verify database connection
log_info "Verifying database connection..."
if ! PGPASSWORD=${POSTGRES_PASSWORD} psql -h ${DB_HOST} -U ${POSTGRES_USER} -d ${DB_NAME} -c '\l' >/dev/null 2>&1; then
    log_error "Cannot connect to database. Please check credentials and permissions"
    exit 1
fi

# Check if database is already initialized
log_info "Checking if database needs initialization..."
if PGPASSWORD=${POSTGRES_PASSWORD} psql -h ${DB_HOST} -U ${POSTGRES_USER} -d ${DB_NAME} -c "SELECT 1 FROM ir_module_module WHERE name='base' AND state='installed'" 2>/dev/null | grep -q 1; then
    log_info "Database already initialized, skipping initialization"
else
    log_info "Initializing fresh database..."
    # Try initialization with increased timeout
    timeout 300s sudo -u ${ODOO_USER} ${VENV_DIR}/bin/python ${ODOO_DIR}/odoo-bin -c ${CONFIG_FILE} \
        -d ${DB_NAME} \
        --db-filter=${DB_NAME} \
        -i base \
        --stop-after-init \
        --without-demo=all \
        --log-level=debug || {
        log_error "Database initialization failed"
        log_error "Checking odoo.log for details..."
        tail -n 50 ${LOG_FILE} || true
        exit 1
    }
fi

log_success "Database initialized successfully"

log_info "Step 17: Setting admin credentials..."
set +e
sudo -u ${ODOO_USER} ${VENV_DIR}/bin/python ${ODOO_DIR}/odoo-bin shell -c ${CONFIG_FILE} -d ${DB_NAME} << 'PYTHON_EOF'
try:
    admin_user = env['res.users'].search([('login', '=', 'admin')])
    if not admin_user:
        admin_user = env['res.users'].browse(2)
    
    admin_user.write({
        'login': 'admin',
        'email': 'admin',
        'password': 'admin'
    })
    env.cr.commit()
    print("Admin credentials set successfully")
except Exception as e:
    print(f"Warning: Could not set admin credentials: {e}")

exit()
PYTHON_EOF
set -e

log_info "Step 18: Starting Odoo service..."
systemctl daemon-reload
systemctl enable odoo

start_attempts=3
for i in $(seq 1 $start_attempts); do
    if systemctl start odoo; then
        log_success "Odoo service started on attempt $i"
        break
    else
        if [[ $i -eq $start_attempts ]]; then
            log_error "Failed to start Odoo after $start_attempts attempts"
            systemctl status odoo --no-pager -l
            journalctl -u odoo -n 20 --no-pager
            exit 1
        else
            log_warning "Odoo start attempt $i failed, retrying in 10 seconds..."
            sleep 10
        fi
    fi
done

log_info "Waiting for services to stabilize..."
sleep 20

log_info "Step 19: Final system verification..."

ODOO_STATUS=$(systemctl is-active odoo 2>/dev/null || echo 'inactive')
NGINX_STATUS=$(systemctl is-active nginx 2>/dev/null || echo 'inactive')
PORT_8069=$(netstat -tlnp 2>/dev/null | grep ':8069.*LISTEN' >/dev/null && echo 'LISTENING' || echo 'NOT LISTENING')
PORT_80=$(netstat -tlnp 2>/dev/null | grep ':80.*LISTEN' >/dev/null && echo 'LISTENING' || echo 'NOT LISTENING')
DB_STATUS=$(PGPASSWORD=${POSTGRES_PASSWORD} psql -h ${DB_HOST} -U ${POSTGRES_USER} -d ${DB_NAME} -c 'SELECT 1' >/dev/null 2>&1 && echo 'OK' || echo 'ERROR')
