# Material Indent Field Explanations

## Required Fields

### `name` - Indent Reference
- **What it is**: Unique identifier for the material indent
- **Format**: IND/PROJ-001, IND/SPARE-001, etc.
- **Examples**: 
  - IND/PROJ-ALPHA-001 (for projects)
  - IND/SPARE-PUMP-001 (for spare parts)
- **Auto-generated**: Yes, but you can specify custom ones during import

### `state` - Status
- **What it is**: Current status of the material indent
- **Values**:
  - **draft**: New indent, can be edited ✏️
  - **submitted**: Sent for approval 📋
  - **approved**: Approved, can create purchase orders ✅
  - **cancel**: Cancelled indent ❌
- **Default**: Always use "draft" for new imports

### `bom_id` - BOM/Product Name
- **What it is**: The main product or BOM you're creating an indent for
- **Examples**:
  - Steel Assembly (for construction project)
  - Pump Kit (for maintenance)
  - Motor Kit (for spare parts)

### `project_id` - Project Name
- **For Project Flow**: Must have a value (e.g., "Alpha Project")
- **For Spare Parts**: Must be empty (leave blank)
- **Examples**:
  - Alpha Construction Project
  - Beta Electrical Project
  - (empty for spare parts)

## Component Fields

### `indent_line_ids/product_id` - Component Product
- **What it is**: The actual product/component you need
- **Examples**: Steel Rod, Bearing, Belt, Cement

### `indent_line_ids/product_name` - Component Display Name
- **What it is**: Display name for the component (usually same as product_id)
- **Examples**: Steel Rod, SKF Bearing 6205, V-Belt A50

### `indent_line_ids/product_qty` - Quantity
- **What it is**: How much of the component you need
- **Format**: Positive decimal number
- **Examples**: 10, 2.5, 0.5

### `indent_line_ids/uom_id` - Unit of Measure
- **What it is**: Unit for the quantity
- **Examples**: Units, Kg, Liters, Meters, Bags, Cubic Meter
### `indent_line_ids/make` - Make/Manufacturer
- **What it is**: The brand or manufacturer of the component
- **Examples**: TATA, SKF, Siemens, Grundfos
- **Auto-pulls**: Yes, if already set in Inventory (Product)

### `indent_line_ids/description_short` - Short Description
- **What it is**: Brief identification for the component
- **Examples**: 12mm Reinforcement, Main Shaft Seal
- **Auto-pulls**: Yes, if already set in Inventory (Product)

## Flow Types

### Project Flow
```csv
name,bom_id,project_id,state
IND/PROJ-001,Steel Assembly,Alpha Project,draft
```
- ✅ Project name required
- ✅ Custom BOM names allowed
- ✅ Components use inventory names

### Spare Parts Flow
```csv
name,bom_id,project_id,state
IND/SPARE-001,Pump Kit,,draft
```
- ❌ Project name must be empty
- ✅ BOM name should match equipment
- ✅ Components are spare parts

## Import Tips

1. **Always use "draft" for state** when importing new indents
2. **Use unique names** for each indent reference
3. **Leave project_id empty** for spare parts (just use empty cell)
4. **Fill project_id** for project-based indents
5. **Ensure all products exist** in Odoo inventory before import