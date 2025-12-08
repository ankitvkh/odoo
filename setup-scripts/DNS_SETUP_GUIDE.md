# DNS Setup - Quick Fix Guide

## What Happened
Your DNS creation script failed with a `ConnectionResetError` when trying to create the DNS zone. This is typically caused by:
1. Transient network issues
2. Google Cloud API connectivity problems
3. Pending DNS transactions blocking new operations

## What Was Fixed

### 1. Added Retry Logic
The script now automatically retries failed gcloud commands up to 3 times with exponential backoff:
- First retry: wait 5 seconds
- Second retry: wait 10 seconds
- Third retry: wait 15 seconds

### 2. Added Transaction Cleanup
Before starting a new DNS transaction, the script now checks for and aborts any pending transactions that might cause conflicts.

### 3. Created Diagnostic Tool
A new script `0_diagnose_gcloud.sh` checks:
- gcloud installation
- Authentication status
- Project configuration
- Network connectivity
- API access
- Pending transactions

## How to Use

### Step 1: Run Diagnostics (Recommended)
```bash
cd /Users/rohitkumar/IdeaProjects/odoo/setup-scripts
sh 0_diagnose_gcloud.sh
```

This will check your gcloud setup and identify any issues.

### Step 2: Retry DNS Setup
```bash
sh 1_dns_creation.sh
```

The script will now automatically:
- Retry on connection failures
- Clean up pending transactions
- Provide better error messages

## Troubleshooting

### If you still get connection errors:

1. **Check your internet connection:**
   ```bash
   ping google.com
   ```

2. **Run gcloud diagnostics:**
   ```bash
   gcloud info --run-diagnostics
   ```

3. **Update gcloud components:**
   ```bash
   gcloud components update
   ```

4. **Re-authenticate:**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

5. **Check if you're behind a proxy:**
   ```bash
   # If yes, configure proxy
   gcloud config set proxy/type http
   gcloud config set proxy/address YOUR_PROXY_ADDRESS
   gcloud config set proxy/port YOUR_PROXY_PORT
   ```

### If DNS zone was partially created:

The script is now idempotent - it will check if resources exist before creating them, so you can safely re-run it.

## Current Configuration

- **Domain:** powertekautomation.in
- **Subdomain:** erp
- **Full Domain:** erp.powertekautomation.in
- **Reserved IP:** 34.14.155.246
- **Region:** asia-south1
- **Project:** magnetic-lore-480113-m4

## Next Steps

After successful DNS setup, you'll need to:
1. Update your domain registrar's nameservers with the ones provided by the script
2. Wait for DNS propagation (can take 24-48 hours)
3. Verify DNS resolution with: `nslookup erp.powertekautomation.in`
