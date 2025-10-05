#!/bin/bash

PROJECT_ID="hypnotic-bounty-469316-a6"     
SQL_INSTANCE_NAME="odoo-postgres"          
REGION="us-central1"                      
DB_NAME="odoo_db"                          
DB_USER="odoo_user"                       
DB_PASSWORD="odoo123"                      
ROOT_PASSWORD="Rasp@2025"


VPC_NETWORK="default"  
PRIVATE_IP_RANGE="google-managed-services-${VPC_NETWORK}"

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

set -e
trap 'log_error "Cloud SQL setup failed at line $LINENO"' ERR

log_info "Setting project and enabling services..."
gcloud config set project ${PROJECT_ID}
gcloud services enable sqladmin.googleapis.com \
    compute.googleapis.com \
    servicenetworking.googleapis.com

log_info "Setting up VPC peering for private IP..."

if ! gcloud compute addresses describe ${PRIVATE_IP_RANGE} --global >/dev/null 2>&1; then
    log_info "Allocating IP range for private services..."
    gcloud compute addresses create ${PRIVATE_IP_RANGE} \
        --global \
        --purpose=VPC_PEERING \
        --prefix-length=16 \
        --network=${VPC_NETWORK}
    log_success "IP range allocated"
else
    log_info "IP range already allocated"
fi

if ! gcloud services vpc-peerings list --network=${VPC_NETWORK} 2>/dev/null | grep -q "servicenetworking.googleapis.com"; then
    log_info "Creating VPC peering connection..."
    gcloud services vpc-peerings connect \
        --service=servicenetworking.googleapis.com \
        --ranges=${PRIVATE_IP_RANGE} \
        --network=${VPC_NETWORK}
    log_success "VPC peering created"
else
    log_info "VPC peering already exists"
fi

if gcloud sql instances describe ${SQL_INSTANCE_NAME} >/dev/null 2>&1; then
    log_warning "Existing instance found. Deleting to recreate with private IP..."
    echo "This will delete your existing Cloud SQL instance and data!"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gcloud sql instances delete ${SQL_INSTANCE_NAME} --quiet
        log_info "Waiting for deletion to complete..."
        sleep 30
    else
        log_info "Keeping existing instance. To migrate to private IP, you need to recreate the instance."
        exit 0
    fi
fi


log_info "Creating Cloud SQL PostgreSQL instance with PRIVATE IP..."
gcloud sql instances create ${SQL_INSTANCE_NAME} \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=${REGION} \
    --network=projects/${PROJECT_ID}/global/networks/${VPC_NETWORK} \
    --no-assign-ip \
    --root-password=${ROOT_PASSWORD} \
    --storage-type=SSD \
    --storage-size=10GB

log_success "Cloud SQL instance created with PRIVATE IP"


log_info "Waiting for instance to be fully ready..."
for i in {1..12}; do
    INSTANCE_STATE=$(gcloud sql instances describe ${SQL_INSTANCE_NAME} --format="value(state)" 2>/dev/null || echo "UNKNOWN")
    if [[ "$INSTANCE_STATE" == "RUNNABLE" ]]; then
        log_success "Instance is ready"
        break
    else
        log_info "Instance state: $INSTANCE_STATE (waiting... $i/12)"
        sleep 15
    fi
done

if [[ "$INSTANCE_STATE" != "RUNNABLE" ]]; then
    log_error "Instance did not reach RUNNABLE state in time"
    exit 1
fi


log_info "Creating Odoo database..."
if ! gcloud sql databases describe ${DB_NAME} --instance=${SQL_INSTANCE_NAME} >/dev/null 2>&1; then
    gcloud sql databases create ${DB_NAME} --instance=${SQL_INSTANCE_NAME}
    log_success "Database ${DB_NAME} created"
else
    log_info "Database ${DB_NAME} already exists"
fi

log_info "Creating database user..."
if ! gcloud sql users describe ${DB_USER} --instance=${SQL_INSTANCE_NAME} >/dev/null 2>&1; then
    gcloud sql users create ${DB_USER} \
        --instance=${SQL_INSTANCE_NAME} \
        --password=${DB_PASSWORD}
    log_success "User ${DB_USER} created"
else
    log_info "User ${DB_USER} already exists, updating password..."
    gcloud sql users set-password ${DB_USER} \
        --instance=${SQL_INSTANCE_NAME} \
        --password=${DB_PASSWORD}
    log_success "User password updated"
fi


CONNECTION_NAME=$(gcloud sql instances describe ${SQL_INSTANCE_NAME} --format='get(connectionName)')
PRIVATE_IP=$(gcloud sql instances describe ${SQL_INSTANCE_NAME} --format='get(ipAddresses[0].ipAddress)')

