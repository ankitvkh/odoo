# Test Import Example - Material Indent

## 📋 File: Minimal_Test_Import.csv

This is a minimal example with **1 project** and **2 spare parts** for testing the Material Indent import functionality.

## 📊 Data Structure

### Project Flow (1 example)
- **Indent Reference**: IND/PROJ-001
- **BOM**: Steel Assembly
- **Project**: Alpha Project ✅ (Required for project flow)
- **Components**: Steel Rod (10 Units), Welding Rod (2 Kg)

### Spare Parts Flow (2 examples)
- **Indent Reference**: IND/SPARE-001
- **BOM**: Pump Kit
- **Project**: *(empty)* ❌ (Must be empty for spare parts)
- **Components**: Bearing (1 Unit)

- **Indent Reference**: IND/SPARE-002
- **BOM**: Motor Kit  
- **Project**: *(empty)* ❌ (Must be empty for spare parts)
- **Components**: Belt (1 Unit)

## 🔑 Key Rules

### For Project Flow:
- **project_id**: Must have a value (e.g., "Alpha Project")
- **bom_id**: Can be any custom name (e.g., "Steel Assembly")

### For Spare Parts Flow:
- **project_id**: Must be empty (no value)
- **bom_id**: Should match equipment/system name

## 🚀 Before Import

### 1. Create BOMs in Odoo
Go to **Manufacturing** → **Products** → **Bills of Materials**
- Create BOM: "Steel Assembly"
- Create BOM: "Pump Kit"  
- Create BOM: "Motor Kit"

### 2. Create Products in Odoo
Go to **Inventory** → **Products** → **Products**
- Create product: "Steel Rod" (Unit: Units)
- Create product: "Welding Rod" (Unit: Kg)
- Create product: "Bearing" (Unit: Units)
- Create product: "Belt" (Unit: Units)

### 3. Create Project in Odoo
Go to **Project** → **Projects**
- Create project: "Alpha Project"

### 4. Configure Units of Measure
Go to **Inventory** → **Configuration** → **Units of Measure**
- Ensure "Units" and "Kg" are available

## 📥 Import Process

1. **Go to Material Indent**
   - Navigate to **Material Indent** → **Indents**

2. **Start Import**
   - Click **Favorites** → **Import Records**

3. **Upload File**
   - Upload `Minimal_Test_Import.csv`

4. **Map Columns**
   - Columns should auto-map if using exact field names
   - Verify mapping is correct

5. **Test Import**
   - Click **Test** to validate data
   - Fix any errors shown

6. **Import Data**
   - Click **Import** to create the records

## ✅ Expected Results

After successful import, you should see:
- **1 Material Indent** for project (IND/PROJ-001) with 2 components
- **2 Material Indents** for spare parts (IND/SPARE-001, IND/SPARE-002) with 1 component each
- All indents in **Draft** status
- Project indent linked to "Alpha Project"
- Spare parts indents with no project link

## 🔧 Troubleshooting

### Common Errors:
- **"BOM not found"**: Create the BOM first in Manufacturing module
- **"Product not found"**: Add the product to Inventory module  
- **"Project not found"**: Create the project in Project module
- **"Invalid UoM"**: Configure Units and Kg in Units of Measure

### Quick Fix:
If you get errors, create the missing items in Odoo first, then retry the import.

---

**This minimal example is perfect for testing the Material Indent import functionality!** 🎯