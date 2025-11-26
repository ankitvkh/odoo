# Dual Flow BOM Implementation Guide

## 🎯 Two BOM Types Implemented

### 1. **Project BOM** 🏗️
- **Custom Product Descriptions**: BOM can have custom/project-specific names
- **Inventory Mapping**: When creating indent, maps to actual inventory products
- **Example**: "Custom Steel Reinforcement Bar" → Maps to → "Steel Rod 12mm" (inventory)

### 2. **Spare Parts BOM** 🔧
- **Exact Name Matching**: Product names must exactly match inventory
- **No Mapping**: Direct 1:1 relationship with inventory products
- **Example**: "SKF Bearing 6308" → Exactly matches → "SKF Bearing 6308" (inventory)

## 📊 BOM Structure

### Project BOM Example:
```
BOM: Steel Building Assembly (Project: Alpha Construction)
├── Custom Steel Reinforcement Bar (50 Units) → Steel Rod 12mm
├── Project Welding Material (5 Kg) → Welding Rod E6013  
└── Anti-Rust Coating (2 Liters) → Primer Paint
```

### Spare Parts BOM Example:
```
BOM: Pump Maintenance Kit (No Project)
├── SKF Bearing 6308 (2 Units) → SKF Bearing 6308
├── Mechanical Seal 40mm (1 Unit) → Mechanical Seal 40mm
└── V-Belt B50 (1 Unit) → V-Belt B50
```

## 🔧 Implementation Details

### New Fields Added:

#### BOM Level:
- **bom_flow_type**: Project or Spare Parts
- **project_id**: Required for project BOMs
- **project_reference**: Additional project code

#### BOM Line Level:
- **custom_product_description**: Custom name (project) or exact name (spare)
- **inventory_product_id**: Maps to actual inventory product
- **Validation**: Ensures spare parts names match exactly

#### Material Indent Line Level:
- **custom_description**: Original BOM description
- **product_id**: Actual inventory product to procure
- **flow_type**: Inherited from BOM

### Validation Rules:

#### Project BOM:
- ✅ Custom descriptions allowed
- ✅ Must map to valid inventory products
- ✅ Project reference required

#### Spare Parts BOM:
- ❌ Custom descriptions must match inventory exactly
- ✅ Direct inventory product reference
- ❌ No project reference allowed

## 🚀 Workflow

### Project BOM Workflow:
1. **Create BOM** with flow type "Project"
2. **Add Project** reference
3. **Add Components** with custom descriptions
4. **Map to Inventory** products
5. **Create Indent** → Uses inventory product names
6. **Generate PO** → Procures actual inventory items

### Spare Parts BOM Workflow:
1. **Create BOM** with flow type "Spare Parts"
2. **Add Components** with exact inventory names
3. **Validate** names match inventory
4. **Create Indent** → Direct inventory reference
5. **Generate PO** → Procures exact spare parts

## 📋 Import Template

### CSV Format:
```csv
product_tmpl_id,bom_flow_type,project_id,bom_line_ids/custom_product_description,bom_line_ids/inventory_product_id,bom_line_ids/product_qty
Steel Building Assembly,project,Alpha Project,Custom Steel Bar,Steel Rod 12mm,50
Pump Kit,spare,,SKF Bearing 6308,SKF Bearing 6308,2
```

### Field Mapping:
- **product_tmpl_id**: Main BOM product
- **bom_flow_type**: "project" or "spare"
- **project_id**: Project name (empty for spare)
- **custom_product_description**: Custom name or exact name
- **inventory_product_id**: Actual inventory product
- **product_qty**: Required quantity

## 🎨 Visual Indicators

### In BOM Form:
- **Blue highlight**: Project BOM lines (custom descriptions allowed)
- **Orange highlight**: Spare Parts BOM lines (exact match required)

### In Material Indent:
- **BOM Description**: Shows original custom name
- **Inventory Product**: Shows actual product to procure
- **Inventory Name**: Shows inventory product name

## ✅ Benefits

### Project BOM Benefits:
- 🎯 **Flexible Naming**: Use project-specific terminology
- 🔄 **Inventory Mapping**: Automatic mapping to procurement items
- 📋 **Project Tracking**: Link to specific projects
- 📊 **Custom Reporting**: Project-based material analysis

### Spare Parts BOM Benefits:
- 🎯 **Exact Matching**: No confusion with part numbers
- 🔧 **Maintenance Focus**: Direct spare parts management
- 📦 **Inventory Sync**: Perfect alignment with stock
- 🚀 **Quick Procurement**: Direct purchase order generation

## 🔍 Example Scenarios

### Construction Project:
```
BOM: "Office Building Foundation"
Project: "Corporate HQ Construction"
Components:
- "High-Grade Cement Mix" → "Portland Cement 50kg"
- "Reinforcement Steel Bars" → "Steel Rod 16mm"
- "Waterproofing Compound" → "Waterproof Membrane"
```

### Equipment Maintenance:
```
BOM: "Centrifugal Pump Overhaul Kit"
No Project (Spare Parts)
Components:
- "SKF Bearing 6308" → "SKF Bearing 6308" (exact match)
- "Viton Seal 40x60x10" → "Viton Seal 40x60x10" (exact match)
- "Stainless Steel Impeller" → "Stainless Steel Impeller" (exact match)
```

## 🛠️ Configuration Steps

1. **Install Module**: Install material_indent module
2. **Configure Products**: Set up inventory products
3. **Create Projects**: Set up projects (for project BOMs)
4. **Create BOMs**: Choose appropriate flow type
5. **Add Components**: Use custom names (project) or exact names (spare)
6. **Test Workflow**: Create indents and verify mapping

This dual-flow implementation provides maximum flexibility while maintaining data integrity for both project-based and maintenance scenarios! 🎉