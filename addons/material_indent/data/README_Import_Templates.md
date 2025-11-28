# Material Indent Import Templates

This directory contains various Excel/CSV templates for importing Material Indent data into Odoo.

## Available Templates

### 1. **Material_Indent_Import_Template.csv**
- **Purpose**: Basic template with user-friendly column names
- **Best for**: Manual data entry and small imports
- **Features**: Simple format, easy to understand

### 2. **material_indent_import_template.csv**
- **Purpose**: Technical template using Odoo external ID format
- **Best for**: System integration and automated imports
- **Features**: Uses external IDs for reliable data linking

### 3. **Material_Indent_Template_Project_Flow.csv**
- **Purpose**: Specialized template for project-based material indents
- **Best for**: Construction, engineering, and project-based industries
- **Features**: Includes project references and construction materials

### 4. **Material_Indent_Template_Spare_Parts.csv**
- **Purpose**: Template for spare parts and maintenance indents
- **Best for**: Manufacturing, maintenance, and equipment management
- **Features**: Focuses on spare parts, bearings, seals, and maintenance items

### 5. **Simple_Material_Indent_Template.csv**
- **Purpose**: Simplified template with minimal columns
- **Best for**: Quick imports and basic use cases
- **Features**: User-friendly headers, minimal complexity

## How to Use These Templates

### Step 1: Choose the Right Template
- **New users**: Start with `Simple_Material_Indent_Template.csv`
- **Project management**: Use `Material_Indent_Template_Project_Flow.csv`
- **Maintenance teams**: Use `Material_Indent_Template_Spare_Parts.csv`
- **System integration**: Use `material_indent_import_template.csv`

### Step 2: Prepare Your Data
1. Download the appropriate template
2. Open in Excel or Google Sheets
3. Replace sample data with your actual data
4. Ensure all referenced items exist in Odoo:
   - BOMs must be created first
   - Products must exist in inventory
   - Projects must be set up (for project flow)
   - Units of measure must be configured

### Step 3: Validate Your Data
- Check that all product codes exist
- Verify BOM references are correct
- Ensure quantities are positive numbers
- Confirm units of measure match product settings

### Step 4: Import into Odoo
1. Go to **Material Indent** → **Indents**
2. Click **Favorites** → **Import Records**
3. Upload your CSV file
4. Map columns if using custom headers
5. Test with a few records first
6. Import all data

## Column Mapping Guide

### Standard Odoo Fields
| Template Column | Odoo Field | Description |
|----------------|------------|-------------|
| name | name | Indent reference number |
| bom_id | bom_id | Reference to Bill of Materials |
| project_id | project_id | Project reference (optional) |
| state | state | Status: draft/submitted/approved/cancel |

### Line Fields (for indent items)
| Template Column | Odoo Field | Description |
|----------------|------------|-------------|
| indent_line_ids/product_id | product_id | Product reference |
| indent_line_ids/product_name | product_name | Product display name |
| indent_line_ids/product_qty | product_qty | Required quantity |
| indent_line_ids/uom_id | uom_id | Unit of measure |

## Data Format Examples

### External ID Format (System Integration)
```csv
name,bom_id/id,indent_line_ids/product_id/id
IND/001,__export__.mrp_bom_1,__export__.product_product_1
```

### Name-Based Format (User Friendly)
```csv
name,bom_id,indent_line_ids/product_id
IND/001,[BOM-001] Construction BOM,[STEEL-ROD] Steel Rod 12mm
```

### Code-Based Format (Simple)
```csv
Indent Reference,BOM Code,Product Code
IND/001,BOM-CONSTRUCTION-001,STEEL-ROD-12
```

## Common Issues and Solutions

### Issue: "BOM not found"
**Solution**: Create the BOM first or use correct BOM reference

### Issue: "Product not found"
**Solution**: Ensure product exists with correct internal reference/code

### Issue: "Invalid external ID"
**Solution**: Use format `[CODE] Name` or create external IDs first

### Issue: "Quantity validation error"
**Solution**: Use positive decimal numbers (e.g., 10.5, not 10,5)

### Issue: "UoM mismatch"
**Solution**: Use compatible units of measure for each product

## Best Practices

1. **Start Small**: Import 5-10 records first to test the format
2. **Use Consistent Naming**: Keep product codes and BOM references consistent
3. **Validate References**: Ensure all BOMs and products exist before import
4. **Backup Data**: Always backup before large imports
5. **Test Environment**: Test imports in development environment first

## Sample Data Scenarios

### Construction Project
- Steel rods, cement, sand, bricks
- Project-based flow with custom BOM names
- Quantities in various units (tons, bags, cubic meters)

### Manufacturing Maintenance
- Bearings, seals, belts, lubricants
- Spare parts flow with exact name matching
- Standard industrial part numbers

### Electrical Installation
- Wires, conduits, switches, panels
- Project-based with electrical specifications
- Length-based quantities (meters, feet)

## Support and Documentation

- **Full Guide**: See `Material_Indent_Import_Guide.md` for detailed instructions
- **Field Reference**: Check Odoo documentation for field specifications
- **Import Wizard**: Use Odoo's built-in import wizard for column mapping
- **Error Logs**: Check import logs for specific error messages

## File Formats Supported

- **CSV**: Comma-separated values (recommended)
- **Excel**: .xlsx format (converted to CSV during import)
- **TSV**: Tab-separated values
- **Encoding**: UTF-8 recommended for international characters

---

**Note**: Always test imports with sample data before importing production data. Keep backups of your original files and database.