# Material Indent Import Guide

## Overview
This guide explains how to import Material Indent data into Odoo using Excel/CSV files.

## File Format
The import file should be in CSV format with the following columns:

### Required Fields

| Column Name | Description | Example | Notes |
|-------------|-------------|---------|-------|
| **name** | Indent Reference | IND/PROJ-001 | Unique identifier for the indent |
| **bom_id/id** | BOM External ID | __export__.mrp_bom_1 | Reference to existing BOM |
| **state** | Status | draft | Values: draft, submitted, approved, cancel |

### Optional Fields

| Column Name | Description | Example | Notes |
|-------------|-------------|---------|-------|
| **project_id/id** | Project External ID | __export__.project_project_1 | Only for project flow type |
| **company_id/id** | Company External ID | __export__.res_company_1 | Defaults to current company |

### Line Fields (One2many)

| Column Name | Description | Example | Notes |
|-------------|-------------|---------|-------|
| **indent_line_ids/product_id/id** | Product External ID | __export__.product_product_1 | Reference to existing product |
| **indent_line_ids/product_name** | Product Name | Steel Rod 12mm | Preserved inventory name |
| **indent_line_ids/product_qty** | Quantity | 10.0 | Numeric value |
| **indent_line_ids/uom_id/id** | UoM External ID | __export__.uom_uom_1 | Unit of measure |

## Import Methods

### Method 1: Using External IDs (Recommended for System Integration)

```csv
name,bom_id/id,project_id/id,state,indent_line_ids/product_id/id,indent_line_ids/product_name,indent_line_ids/product_qty,indent_line_ids/uom_id/id
IND/00001,__export__.mrp_bom_1,__export__.project_project_1,draft,__export__.product_product_1,Steel Rod 12mm,10.0,__export__.uom_uom_1
```

### Method 2: Using Names (User-Friendly)

```csv
name,bom_id,project_id,state,indent_line_ids/product_id,indent_line_ids/product_name,indent_line_ids/product_qty,indent_line_ids/uom_id
IND/PROJ-001,BOM/STEEL/001,Project Alpha,draft,[STEEL-ROD-12] Steel Rod 12mm,Steel Rod 12mm,10.0,Units
```

## Step-by-Step Import Process

### 1. Prepare Your Data
- Ensure all referenced BOMs exist in the system
- Verify all products are created with correct codes
- Check that projects exist (for project flow type)
- Validate units of measure

### 2. Format Your Excel File
- Use the provided template as a starting point
- Fill in your actual data
- Save as CSV format

### 3. Import in Odoo
1. Go to **Material Indent** → **Indents**
2. Click **Favorites** → **Import Records**
3. Upload your CSV file
4. Map the columns if needed
5. Test import with a few records first
6. Import all data

## Data Validation Rules

### Material Indent Header
- **name**: Must be unique
- **bom_id**: Must reference an existing BOM
- **state**: Must be one of: draft, submitted, approved, cancel
- **project_id**: Required if BOM flow type is 'project'

### Material Indent Lines
- **product_id**: Must reference an existing product
- **product_qty**: Must be greater than 0
- **uom_id**: Must be compatible with product UoM category

## Flow Types

### Project Flow
- BOM can have custom names
- Project reference is required
- Indent lines use actual inventory product names
- Example: Construction project with custom BOM names

### Spare Parts Flow
- BOM name must match product name exactly
- No project reference needed
- Maintains name consistency throughout process
- Example: Machine spare parts inventory

## Common Import Errors and Solutions

### Error: "BOM not found"
**Solution**: Ensure the BOM reference exists in the system or create it first.

### Error: "Product not found"
**Solution**: Create the product in inventory or use correct product reference.

### Error: "Invalid quantity"
**Solution**: Ensure quantity is a positive number.

### Error: "UoM category mismatch"
**Solution**: Use compatible unit of measure for the product.

## Sample Data Templates

### Template 1: Project-Based Indent
```csv
name,bom_id,project_id,state,indent_line_ids/product_id,indent_line_ids/product_name,indent_line_ids/product_qty,indent_line_ids/uom_id
IND/PROJ-001,BOM/CONSTRUCTION/001,Project Alpha,draft,[STEEL-ROD] Steel Rod 12mm,Steel Rod 12mm,50.0,Units
IND/PROJ-001,BOM/CONSTRUCTION/001,Project Alpha,draft,[CEMENT] Cement 50kg,Cement Bag 50kg,20.0,Bags
```

### Template 2: Spare Parts Indent
```csv
name,bom_id,state,indent_line_ids/product_id,indent_line_ids/product_name,indent_line_ids/product_qty,indent_line_ids/uom_id
IND/SPARE-001,BOM/MACHINE-A/SPARE,draft,[BEARING-001] Bearing 6205,Bearing 6205,4.0,Units
IND/SPARE-001,BOM/MACHINE-A/SPARE,draft,[BELT-001] V-Belt A50,V-Belt A50,2.0,Units
```

## Best Practices

1. **Start Small**: Import a few records first to test the format
2. **Use External IDs**: For system integration, use external IDs for reliability
3. **Validate Data**: Check all references exist before importing
4. **Backup First**: Always backup your database before large imports
5. **Test Environment**: Test imports in a development environment first

## Troubleshooting

### Import Fails Completely
- Check CSV format and encoding (UTF-8 recommended)
- Verify column headers match exactly
- Ensure no special characters in data

### Partial Import Success
- Check error messages for specific line issues
- Validate data types (numbers, dates, etc.)
- Verify all referenced records exist

### Performance Issues
- Import in smaller batches (100-500 records)
- Avoid importing during peak usage hours
- Consider using external ID references for better performance

## Support

For additional help with imports:
1. Check Odoo documentation on data import
2. Use the built-in import wizard for column mapping
3. Contact your system administrator for complex imports