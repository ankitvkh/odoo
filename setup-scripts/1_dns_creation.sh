#!/bin/bash

# Configuration 
DOMAIN_NAME="rasptechnologies.co.in"          
SUBDOMAIN="odoo"                            
RESERVED_IP_NAME="odoo-reserved-ip"         
DNS_ZONE_NAME="odoo-zone"                  
REGION="us-central1"                        
PROJECT_ID="hypnotic-bounty-469316-a6"     


FULL_DOMAIN="${SUBDOMAIN}.${DOMAIN_NAME}"
DNS_ZONE_DNS_NAME="${DOMAIN_NAME}."

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
trap 'log_error "DNS setup failed at line $LINENO"' ERR

gcloud services enable compute.googleapis.com dns.googleapis.com

log_info "Creating reserved IP address..."
if gcloud compute addresses describe $RESERVED_IP_NAME --region=$REGION >/dev/null 2>&1; then
    log_info "Reserved IP already exists"
else
    gcloud compute addresses create $RESERVED_IP_NAME --region=$REGION
    log_success "Reserved IP created"
fi

RESERVED_IP=$(gcloud compute addresses describe $RESERVED_IP_NAME --region=$REGION --format="value(address)")
log_success "Reserved IP: $RESERVED_IP"

log_info "Creating DNS zone..."
if gcloud dns managed-zones describe $DNS_ZONE_NAME >/dev/null 2>&1; then
    log_info "DNS zone already exists"
else
    gcloud dns managed-zones create $DNS_ZONE_NAME \
        --description="DNS zone for Odoo" \
        --dns-name=$DNS_ZONE_DNS_NAME \
        --visibility=public
    log_success "DNS zone created"
fi

log_info "Creating DNS A record..."
gcloud dns record-sets transaction start --zone=$DNS_ZONE_NAME

EXISTING_IP=$(gcloud dns record-sets list --zone=$DNS_ZONE_NAME --name="${SUBDOMAIN}.${DNS_ZONE_DNS_NAME}" --type=A --format="value(rrdatas[0])" 2>/dev/null || echo "")
if [ -n "$EXISTING_IP" ]; then
    gcloud dns record-sets transaction remove $EXISTING_IP --name="${SUBDOMAIN}.${DNS_ZONE_DNS_NAME}" --type=A --zone=$DNS_ZONE_NAME --ttl=300
fi

gcloud dns record-sets transaction add $RESERVED_IP --name="${SUBDOMAIN}.${DNS_ZONE_DNS_NAME}" --type=A --zone=$DNS_ZONE_NAME --ttl=300
gcloud dns record-sets transaction execute --zone=$DNS_ZONE_NAME

log_success "DNS A record created: $FULL_DOMAIN -> $RESERVED_IP"

NAME_SERVERS=$(gcloud dns managed-zones describe $DNS_ZONE_NAME --format="value(nameServers[])" | tr ';' '\n')

echo ""
echo "============================================="
log_success "DNS SETUP COMPLETED!"
echo "============================================="
