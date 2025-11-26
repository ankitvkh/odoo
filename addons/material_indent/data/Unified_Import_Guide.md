# Material Indent Unified Import Template Guide

## Overview
This guide explains how to use the unified CSV template that includes both project-based and spare parts material indents in a single file.

## Template Structure
Based on your BOM format: **Product | Quantity | BoM Type | Unit of Measure | BoM Lines/Component | BoM Lines/Quantity**

## Files Available

### 1. **Material_Indent_Import_Ready.csv** (Recommended)
- **Purpose**: Ready-to-import format for Odoo
- **Columns**: Odoo field names for direct import
- **Best for**: Direct import into Odoo system

### 2. **Material_Indent_Simple_Template.csv**
- **Purpose**: User-friendly column names
- **Best for**: Manual data preparation before converting to import format

### 3. **Material_Indent_Unified_Template.csv**
- **Purpose**: Matches your BOM structure exactly
- **Best for**: Understanding the relationship between BOMs and Material Indents

## Column Mapping

### Import Ready Format (Material_Indent_Import_Ready.csv)
| Column | Description | Example | Required |
|--------|-------------|---------|----------|
| **name** | Indent Reference | IND/PROJ-ALPHA-001 | Yes |
| **bom_id** | BOM/Product Name | Steel Structure Assembly | Yes |
| **project_id** | Project Name | Alpha Construction Project | For project flow |
| **state** | Status | draft | Yes |
| **indent_line_ids/product_id** | Component Name | Steel Rod 12mm | Yes |
| **indent_line_ids/product_name** | Component Display Name | Steel Rod 12mm | Yes |
| **indent_line_ids/product_qty** | Required Quantity | 50 | Yes |
| **indent_line_ids/uom_id** | Unit of Measure | Units | Yes |

### Simple Format (Material_Indent_Simple_Template.csv)
| Column | Description | Example | Notes |
|--------|-------------|---------|-------|
| **Product Name** | Main BOM Product | Steel Structure Assembly | What you're making |
| **Project Name** | Project Reference | Alpha Construction Project | Empty for spare parts |
| **Component Name** | Required Material | Steel Rod 12mm | What you need |
| **Quantity** | How much needed | 50 | Numeric value |
| **Unit** | Unit of measure | Units | Kg, Liters, Meters, etc. |
| **Flow Type** | project or spare | project | Determines workflow |
| **Indent Reference** | Unique ID | IND/PROJ-ALPHA-001 | Must be unique |
| **Status** | Current state | draft | draft/submitted/approved |

## Flow Types Explained

### Project Flow (project_id required)
- **Use case**: Construction, engineering projects with custom BOMs
- **Example**: Building a steel structure for "Alpha Construction Project"
- **BOM**: Can have custom names different from final product
- **Components**: Use actual inventory product names

### Spare Parts Flow (project_id empty)
- **Use case**: Maintenance, equipment spare parts
- **Example**: Pump maintenance kit, conveyor belt spares
- **BOM**: Name should match the equipment/system
- **Components**: Exact spare part names from inventory

## Sample Data Explanation

### Project Examples
```csv
Product: Steel Structure Assembly
Project: Alpha Construction Project
Components: Steel Rod 12mm (50 Units), Steel Plate 10mm (20 Units)
Flow: project
```

```csv
Product: Electrical Panel Assembly  
Project: Beta Electrical Project
Components: Distribution Board (1 Unit), MCB 32A (12 Units), Copper Wire (50 Meters)
Flow: project
```

### Spare Parts Examples
```csv
Product: Pump Motor Assembly
Project: (empty)
Components: SKF Bearing (2 Units), Mechanical Seal (1 Unit), V-Belt (1 Unit)
Flow: spare
```

```csv
Product: HVAC Unit Maintenance
Project: (empty)  
Components: Air Filter (4 Units), Fan Belt (2 Units), Refrigerant (2 Kg)
Flow: spare
```

## Import Process

### Step 1: Prepare Your Data
1. **Create BOMs first**: Ensure all main products exist as BOMs in Odoo
2. **Create components**: All component products must exist in inventory
3. **Set up projects**: Create projects for project-flow indents
4. **Configure UoMs**: Ensure all units of measure are set up

### Step 2: Fill the Template
1. Use **Material_Indent_Simple_Template.csv** for easy data entry
2. Fill in your actual products, projects, and components
3. Ensure quantities are positive numbers
4. Use consistent naming for products and projects

### Step 3: Convert to Import Format
Convert your simple format to **Material_Indent_Import_Ready.csv** format:
- Copy indent reference to `name` column
- Copy product name to `bom_id` column  
- Copy project name to `project_id` column (empty for spare parts)
- Copy component details to `indent_line_ids/*` columns

### Step 4: Import into Odoo
1. Go to **Material Indent** → **Indents**
2. Click **Favorites** → **Import Records**
3. Upload **Material_Indent_Import_Ready.csv**
4. Map columns (should auto-map if using exact column names)
5. Test with 2-3 records first
6. Import all data

## Data Validation Rules

### Required Data
- All BOMs must exist in Odoo MRP module
- All component products must exist in inventory
- Projects must be created in Project module (for project flow)
- Units of measure must be configured

### Naming Conventions
- **Indent Reference**: Use format IND/TYPE-NAME-001
- **Product Names**: Must match BOM names exactly
- **Component Names**: Must match inventory product names
- **Project Names**: Must match project names in Odoo

### Quantity Rules
- Must be positive decimal numbers
- Use dot (.) for decimals, not comma (,)
- Example: 10.5 ✓, 10,5 ✗

## Common Scenarios

### Construction Project
```csv
Product: Building Foundation
Project: Residential Complex Phase 1
Components: Cement (100 Bags), Steel Rods (500 Units), Sand (10 Cubic Meter)
```

### Manufacturing Maintenance
```csv
Product: Production Line A Maintenance
Project: (empty)
Components: Conveyor Belt (5 Meters), Motor Bearings (4 Units), Lubricant (2 Liters)
```

### Electrical Installation
```csv
Product: Office Electrical Setup
Project: Corporate Office Renovation
Components: Cables (200 Meters), Switches (25 Units), Panels (3 Units)
```

## Troubleshooting

### Common Errors

**"BOM not found"**
- Solution: Create the BOM in MRP module first
- Check: BOM name matches exactly with `bom_id` column

**"Product not found"**  
- Solution: Create component products in inventory
- Check: Product names match exactly with `indent_line_ids/product_id`

**"Project not found"**
- Solution: Create project in Project module
- Check: Project name matches exactly with `project_id`

**"Invalid quantity"**
- Solution: Use positive decimal numbers only
- Check: No text, negative numbers, or special characters

**"UoM not found"**
- Solution: Configure unit of measure in Inventory settings
- Check: UoM name matches exactly with `indent_line_ids/uom_id`

### Import Tips

1. **Start small**: Import 5-10 records first to test
2. **Check references**: Verify all BOMs, products, and projects exist
3. **Use consistent naming**: Keep names exactly as they appear in Odoo
4. **Backup first**: Always backup database before large imports
5. **Test environment**: Test in development environment first

## Best Practices

### Data Preparation
- Use Excel to prepare data, save as CSV for import
- Keep a master list of all BOMs, products, and projects
- Use consistent naming conventions across all modules
- Validate data before import using Odoo's test import feature

### Workflow Management
- Import in logical order: BOMs → Products → Projects → Material Indents
- Group related indents together (same project, same equipment)
- Use meaningful indent reference numbers for easy tracking
- Set appropriate status (usually 'draft' for new imports)

### Maintenance
- Regular cleanup of unused BOMs and products
- Update component availability before creating indents
- Review and approve indents before generating purchase orders
- Track indent status and purchase order generation

---

**Note**: This unified template allows you to manage both project-based and spare parts material indents in a single import file, making it easier to maintain and process bulk data.