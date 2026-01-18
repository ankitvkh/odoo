#!/bin/bash

PROJECT_ID="magnetic-lore-480113-m4"    
VM_NAME="erp-powertek"                      
ZONE="asia-south1-a"                       
MACHINE_TYPE="e2-medium"                  
NETWORK="default"                          
RESERVED_IP_NAME="erp-reserved-ip"        
STARTUP_SCRIPT="./Startup_Script.sh"

DOMAIN_NAME="erp.powertekautomation.in"  
ADMIN_EMAIL="mkumar@powertekautomation.in" 


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
trap 'log_error "VM creation failed at line $LINENO"' ERR


gcloud services enable compute.googleapis.com

log_info "Getting reserved IP from DNS setup..."
REGION=$(echo $ZONE | sed 's/-[a-z]$//')
if ! RESERVED_IP=$(gcloud compute addresses describe $RESERVED_IP_NAME --region=$REGION --format="value(address)" 2>/dev/null); then
    log_error "Reserved IP not found. Please run ./DNS.sh first"
    exit 1
fi
log_success "Found reserved IP: $RESERVED_IP"


log_info "Setting up firewall rules for dual port access..."
FIREWALL_RULES=(
    "allow-http:tcp:80"
    "allow-https:tcp:443"
    "allow-erp:tcp:8069"
    "allow-erp-longpolling:tcp:8072"
)

for rule_spec in "${FIREWALL_RULES[@]}"; do
    IFS=':' read -r rule_name protocol port <<< "$rule_spec"
    
    if ! gcloud compute firewall-rules describe "$rule_name" >/dev/null 2>&1; then
        gcloud compute firewall-rules create "$rule_name" \
            --allow "${protocol}:${port}" \
            --source-ranges "0.0.0.0/0" \
            --target-tags "erp-server" \
            --description "Allow ${protocol} traffic on port ${port} for Odoo"
        log_success "Created firewall rule: $rule_name"
    else
        log_info "Firewall rule already exists: $rule_name"
    fi
done


if gcloud compute instances describe ${VM_NAME} --zone=${ZONE} >/dev/null 2>&1; then
    log_warning "Deleting existing VM: $VM_NAME"
    gcloud compute instances delete ${VM_NAME} --zone=${ZONE} --quiet
    sleep 10
fi


if [[ ! -f "$STARTUP_SCRIPT" ]]; then
    exit 1
fi


RESTORE_DATA="true" # Set to "true" to restore the latest backup

log_info "Creating VM with SQL erp installation startup script..."
gcloud compute instances create ${VM_NAME} \
    --zone=${ZONE} \
    --machine-type=${MACHINE_TYPE} \
    --network=${NETWORK} \
    --address=${RESERVED_IP_NAME} \
    --tags=erp-server \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=30GB \
    --scopes=storage-full \
    --metadata RESTORE_DATA=${RESTORE_DATA},DOMAIN_NAME=${DOMAIN_NAME},ADMIN_EMAIL=${ADMIN_EMAIL} \
    --metadata-from-file startup-script=${STARTUP_SCRIPT}

log_success "VM created successfully (Restore Flag: ${RESTORE_DATA})"

REGION=$(echo $ZONE | sed 's/-[a-z]$//')
SCHEDULE_NAME="erp-power-schedule"

log_info "Setting up VM Power Schedule (Start: 03:30 UTC, Stop: 15:30 UTC)..."

# Create the resource policy if it doesn't exist
if ! gcloud compute resource-policies describe $SCHEDULE_NAME --region=$REGION >/dev/null 2>&1; then
    gcloud compute resource-policies create instance-schedule $SCHEDULE_NAME \
        --region=$REGION \
        --vm-start-schedule="0 9 * * 1-6" \
        --vm-stop-schedule="0 21 * * 1-6" \
        --timezone="Asia/Kolkata" \
        --description="Start at 9 AM IST, Stop at 9 PM IST (Mon-Sat)"
    log_success "Created resource policy: $SCHEDULE_NAME"
else
    log_info "Resource policy already exists: $SCHEDULE_NAME"
fi

# Attach the policy to the instance
log_info "Attaching schedule to VM..."
gcloud compute instances add-resource-policies ${VM_NAME} \
    --zone=${ZONE} \
    --resource-policies=$SCHEDULE_NAME

log_success "VM Power Schedule attached successfully"


VM_EXTERNAL_IP=$(gcloud compute instances describe ${VM_NAME} --zone=${ZONE} --format='get(networkInterfaces[0].accessConfigs[0].natIP)')
