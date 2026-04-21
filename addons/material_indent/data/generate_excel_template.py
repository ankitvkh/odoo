#!/usr/bin/env python3
"""
Generate Unified Material Indent Import Template
Based on BOM structure: Product | Quantity | BoM Type | Unit of Measure | BoM Lines/Component | BoM Lines/Quantity
Creates a single CSV with both project and spare parts examples
"""

import csv
import os

def create_unified_template():
    """Create unified Material Indent template with project and spare parts in one file"""
    
    # Unified template with both project and spare parts
    unified_data = [
        # Headers
        ['name', 'bom_id', 'project_id', 'state', 'indent_line_ids/product_id', 'indent_line_ids/product_name', 'indent_line_ids/product_qty', 'indent_line_ids/uom_id', 'indent_line_ids/make', 'indent_line_ids/description_short'],
        
        # Project Flow Examples - Construction
        ['IND/PROJ-ALPHA-001', 'Steel Structure Assembly', 'Alpha Construction Project', 'draft', 'Steel Rod 12mm', 'Steel Rod 12mm', '50', 'Units', 'TATA', 'Reinforcement Bar'],
        ['IND/PROJ-ALPHA-001', 'Steel Structure Assembly', 'Alpha Construction Project', 'draft', 'Steel Plate 10mm', 'Steel Plate 10mm', '20', 'Units', 'JSW', 'Base Plate'],
        ['IND/PROJ-ALPHA-001', 'Steel Structure Assembly', 'Alpha Construction Project', 'draft', 'Welding Rod E6013', 'Welding Rod E6013', '5', 'Kg', 'Adani', 'Joining material'],
        
        # Spare Parts Flow Examples - Pump Maintenance
        ['IND/SPARE-PUMP-001', 'Pump Motor Assembly', '', 'draft', 'SKF Bearing 6308', 'SKF Bearing 6308', '2', 'Units', 'SKF', 'Drive end bearing'],
        ['IND/SPARE-PUMP-001', 'Pump Motor Assembly', '', 'draft', 'Mechanical Seal 40mm', 'Mechanical Seal 40mm', '1', 'Units', 'Grundfos', 'Main shaft seal'],
    ]
    
    # Simple user-friendly template
    simple_data = [
        # Headers
        ['Product Name', 'Project Name', 'Component Name', 'Quantity', 'Unit', 'Make', 'Description', 'Flow Type', 'Indent Reference', 'Status'],
        
        # Project Examples
        ['Steel Structure Assembly', 'Alpha Construction Project', 'Steel Rod 12mm', '50', 'Units', 'TATA', 'Reinforcement Bar', 'project', 'IND/PROJ-ALPHA-001', 'draft'],
        ['Steel Structure Assembly', 'Alpha Construction Project', 'Steel Plate 10mm', '20', 'Units', 'JSW', 'Base Plate', 'project', 'IND/PROJ-ALPHA-001', 'draft'],
        
        # Spare Parts Examples
        ['Pump Motor Assembly', '', 'SKF Bearing 6308', '2', 'Units', 'SKF', 'Drive end bearing', 'spare', 'IND/SPARE-PUMP-001', 'draft'],
    ]
    
    # Create unified import-ready template
    with open('Material_Indent_Unified_Import.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for row in unified_data:
            writer.writerow(row)
    print("Created: Material_Indent_Unified_Import.csv")
    
    # Create simple user-friendly template
    with open('Material_Indent_Simple_Format.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for row in simple_data:
            writer.writerow(row)
    print("Created: Material_Indent_Simple_Format.csv")

def create_inventory_template():
    """Create Inventory (Product Template) import template"""
    inventory_data = [
        # Headers
        ['name', 'default_code', 'type', 'categ_id', 'list_price', 'standard_price', 'uom_id', 'make', 'description_short'],
        ['Steel Rod 12mm', 'ST-ROD-12', 'product', 'All / Raw Materials', '100', '80', 'Units', 'TATA', '12mm Reinforcement Bar'],
        ['Steel Plate 10mm', 'ST-PLT-10', 'product', 'All / Raw Materials', '500', '400', 'Units', 'JSW', '10mm Mild Steel Plate'],
        ['SKF Bearing 6308', 'BRG-6308', 'product', 'All / Spare Parts', '1200', '1000', 'Units', 'SKF', 'Deep Groove Ball Bearing'],
        ['Mechanical Seal 40mm', 'SEAL-40', 'product', 'All / Spare Parts', '2500', '2000', 'Units', 'Grundfos', 'Water Pump Seal'],
    ]
    
    with open('Inventory_Import_Template.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for row in inventory_data:
            writer.writerow(row)
    print("Created: Inventory_Import_Template.csv")

def create_bom_template():
    """Create BOM Structure import template"""
    bom_data = [
        # Headers
        ['product_tmpl_id', 'bom_flow_type', 'project_id', 'bom_line_ids/product_id', 'bom_line_ids/product_qty', 'bom_line_ids/custom_product_description'],
        ['Steel Structure Assembly', 'project', 'Alpha Construction Project', 'Steel Rod 12mm', '50', 'Project Reinforcement'],
        ['Steel Structure Assembly', 'project', 'Alpha Construction Project', 'Steel Plate 10mm', '20', 'Project Base Plates'],
        ['Pump Motor Assembly', 'spare', '', 'SKF Bearing 6308', '2', 'SKF Bearing 6308'],
        ['Pump Motor Assembly', 'spare', '', 'Mechanical Seal 40mm', '1', 'Mechanical Seal 40mm'],
    ]
    # Note: 'make' and 'description_short' in BOM lines are related fields from product_id
    # so they are usually imported into Product Template, not BoM Line directly.
    
    with open('BOM_Structure_Import_Template.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for row in bom_data:
            writer.writerow(row)
    print("Created: BOM_Structure_Import_Template.csv")

def update_instructions():
    """Update instructions and summary"""
    instructions = """
# Material Indent & Inventory Import Templates

## 📂 Core Templates:
1. **Inventory_Import_Template.csv** - Load Products with Make and Description
2. **BOM_Structure_Import_Template.csv** - Load Bill of Materials
3. **Material_Indent_Unified_Import.csv** - Ready-to-import Indents
4. **Material_Indent_Simple_Format.csv** - User-friendly data preparation

## 🆕 New Fields Added:
- **Make**: Manufacturer/Brand (e.g., TATA, SKF, Siemens)
- **Description**: Short identification (e.g., 12mm Rod, Ball Bearing)

## 🚀 How to Use:
1. **Import Inventory First**: Use `Inventory_Import_Template.csv` to load products with their Make and Description.
2. **Import BOMs**: Use `BOM_Structure_Import_Template.csv` to link products into BOMs.
3. **Import Indents**: Use `Material_Indent_Unified_Import.csv` to create material indents.

## 💡 Pro Tip:
The 'Make' and 'Description' fields in BOM and Indent lines are automatically pulled from the Inventory (Product) settings. When you import products using the Inventory template, these values will show up everywhere else!
"""
    with open('Import_Templates_Guide.txt', 'w') as f:
        f.write(instructions)
    print("Created: Import_Templates_Guide.txt")

if __name__ == "__main__":
    create_unified_template()
    create_inventory_template()
    create_bom_template()
    update_instructions()
    print("\n✅ All templates updated with Make and Description fields!")