#!/bin/bash

# DNS Setup Troubleshooting Guide
# This script helps diagnose and fix common gcloud DNS setup issues

echo "=== Google Cloud DNS Setup Diagnostics ==="
echo ""

# Check gcloud installation
echo "1. Checking gcloud installation..."
if command -v gcloud &> /dev/null; then
    echo "✓ gcloud is installed"
    gcloud version
else
    echo "✗ gcloud is NOT installed"
    echo "  Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo ""
echo "2. Checking gcloud authentication..."
ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null)
if [ -n "$ACCOUNT" ]; then
    echo "✓ Authenticated as: $ACCOUNT"
else
    echo "✗ Not authenticated"
    echo "  Run: gcloud auth login"
    exit 1
fi

echo ""
echo "3. Checking active project..."
PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ -n "$PROJECT" ]; then
    echo "✓ Active project: $PROJECT"
else
    echo "✗ No active project set"
    echo "  Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo ""
echo "4. Checking network connectivity..."
if ping -c 1 google.com &> /dev/null; then
    echo "✓ Internet connection is working"
else
    echo "✗ No internet connection"
    echo "  Check your network connection"
    exit 1
fi

echo ""
echo "5. Testing gcloud API connectivity..."
if gcloud services list --enabled --limit=1 &> /dev/null; then
    echo "✓ Can connect to Google Cloud APIs"
else
    echo "✗ Cannot connect to Google Cloud APIs"
    echo "  This might be a firewall or proxy issue"
    echo "  Run: gcloud info --run-diagnostics"
    exit 1
fi

echo ""
echo "6. Checking required APIs..."
COMPUTE_ENABLED=$(gcloud services list --enabled --filter="name:compute.googleapis.com" --format="value(name)" 2>/dev/null)
DNS_ENABLED=$(gcloud services list --enabled --filter="name:dns.googleapis.com" --format="value(name)" 2>/dev/null)

if [ -n "$COMPUTE_ENABLED" ]; then
    echo "✓ Compute API is enabled"
else
    echo "⚠ Compute API is NOT enabled (will be enabled during setup)"
fi

if [ -n "$DNS_ENABLED" ]; then
    echo "✓ DNS API is enabled"
else
    echo "⚠ DNS API is NOT enabled (will be enabled during setup)"
fi

echo ""
echo "7. Checking for pending transactions..."
DNS_ZONE_NAME="erp-zone"
if gcloud dns managed-zones describe $DNS_ZONE_NAME &> /dev/null; then
    echo "✓ DNS zone '$DNS_ZONE_NAME' exists"
    
    # Check for pending transactions
    if gcloud dns record-sets transaction describe --zone=$DNS_ZONE_NAME &> /dev/null; then
        echo "⚠ WARNING: There is a pending DNS transaction!"
        echo "  Aborting it now..."
        gcloud dns record-sets transaction abort --zone=$DNS_ZONE_NAME
        echo "  Transaction aborted. You can now retry the setup."
    else
        echo "✓ No pending DNS transactions"
    fi
else
    echo "⚠ DNS zone '$DNS_ZONE_NAME' does not exist yet (will be created during setup)"
fi

echo ""
echo "=== Diagnostics Complete ==="
echo ""
echo "If all checks passed, you can retry the DNS setup script."
echo "If you're still experiencing connection issues, try:"
echo "  1. Run: gcloud config set proxy/type http"
echo "  2. Run: gcloud config set proxy/address YOUR_PROXY_ADDRESS"
echo "  3. Run: gcloud config set proxy/port YOUR_PROXY_PORT"
echo "  4. Or run: gcloud info --run-diagnostics"
