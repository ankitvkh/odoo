# BOM Material Indent Import Instructions

## ✅ No Separate Material Indent Page!

The material indent functionality is now **integrated directly into the BOM form** in Manufacturing.

## 📍 Where to Find It

1. Go to **Manufacturing** → **Bills of Materials**
2. Open any BOM or create a new one
3. Scroll down to see **"Material Indent Configuration"** and **"Material Indent Lines"** sections

## 📊 Import Template: Final_BOM_Import_Template.csv

```csv
bom_flow_type,project_id,material_indent_line_ids/indent_reference,material_indent_line_ids/product_id,material_indent_line_ids/product_qty,material_indent_line_ids/state
project,Alpha Project,IND/PROJ-001,Steel Rod,10,draft
project,Alpha Project,IND/PROJ-001,Welding Rod,2,draft
spare,,IND/SPARE-001,Bearing,1,draft
spare,,IND/SPARE-002,Belt,1,draft
```

## 🔧 How to Import

### Method 1: Direct Import in BOM Form
1. Open a BOM in Manufacturing
2. Click **Favorites** → **Import Records**
3. Upload the CSV file
4. Map the columns
5. Import

### Method 2: Use Load Components Button
1. Open a BOM that has components
2. Click **"Load Components from BOM"** button
3. It will auto-populate material indent lines from BOM components

## 📋 Field Explanations

### BOM Level Fields:
- **bom_flow_type**: `project` or `spare`
- **project_id**: Project name (empty for spare parts)

### Material Indent Lines:
- **indent_reference**: IND/PROJ-001, IND/SPARE-001, etc.
- **product_id**: Product name (Steel Rod, Bearing, etc.)
- **product_qty**: Quantity needed
- **state**: `draft`, `submitted`, `approved`, `cancel`

## 🎯 Flow Types

### Project Flow
```csv
bom_flow_type,project_id
project,Alpha Project
```
- ✅ Project name required
- ✅ Custom BOM names allowed

### Spare Parts Flow  
```csv
bom_flow_type,project_id
spare,
```
- ❌ Project name must be empty
- ✅ Equipment/system names

## 🚀 Workflow

1. **Create/Open BOM** in Manufacturing
2. **Set Flow Type** (project or spare)
3. **Add Project** (if project flow)
4. **Import or Load Components**
5. **Review Material Indent Lines**
6. **Generate Purchase Orders**

## ✅ Benefits

- ❌ No separate Material Indent menu
- ✅ Everything in one BOM form
- ✅ Direct import into BOM
- ✅ Auto-load from BOM components
- ✅ Integrated workflow

Now you can manage material indents directly within the BOM form! 🎉