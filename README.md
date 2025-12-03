# Backup and Restore Scripts
Execute the following scripts in order:

1. [backup_to_gcp_bucket.py](setup-scripts/backup-restore/backup_to_gcp_bucket.py)
2. [restore_from_gcp_bucket.py](setup-scripts/backup-restore/restore_from_gcp_bucket.py)

# Create and setup VM with DNS

Execute the following scripts in order:

1. [1_dns_creation.sh](setup-scripts/1_dns_creation.sh)
2. [2_vm_creation.sh](setup-scripts/2_vm_creation.sh)

# Odoo modules to enable

```
Sales (sale_management)
Sale Order Enhancement (sale_order_enhancement)
Inventory (stock)
Manufacturing (mrp)
Purchase (purchase)
Project (project)
Invoicing (account)
Odoo 18 Accounting (om_account_accountant)
Project Task Validations (project_task_validations)
Project Activity Templates (project_activity_template)
Manufacturing BOM Import (bom_pro_max) -- Currently disabled
```

# Manual settings to configure

1. Add new language: Settings -> General Settings -> Languages -> Add English(IN)
2. Enable task dependencies: Settings -> Project -> Task Dependencies (checkbox)
3. Configure main currency: Settings -> Accounting -> Currencies -> Main Currency (dropdown)