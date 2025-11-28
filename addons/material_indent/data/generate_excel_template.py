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
        ['name', 'bom_id', 'project_id', 'state', 'indent_line_ids/product_id', 'indent_line_ids/product_name', 'indent_line_ids/product_qty', 'indent_line_ids/uom_id'],
        
        # Project Flow Examples - Construction
        ['IND/PROJ-ALPHA-001', 'Steel Structure Assembly', 'Alpha Construction Project', 'draft', 'Steel Rod 12mm', 'Steel Rod 12mm', '50', 'Units'],
        ['IND/PROJ-ALPHA-001', 'Steel Structure Assembly', 'Alpha Construction Project', 'draft', 'Steel Plate 10mm', 'Steel Plate 10mm', '20', 'Units'],
        ['IND/PROJ-ALPHA-001', 'Steel Structure Assembly', 'Alpha Construction Project', 'draft', 'Welding Rod E6013', 'Welding Rod E6013', '5', 'Kg'],
        ['IND/PROJ-ALPHA-001', 'Steel Structure Assembly', 'Alpha Construction Project', 'draft', 'Primer Paint', 'Primer Paint', '2', 'Liters'],
        
        ['IND/PROJ-ALPHA-002', 'Concrete Foundation Mix', 'Alpha Construction Project', 'draft', 'Portland Cement 50kg', 'Portland Cement 50kg', '15', 'Bags'],
        ['IND/PROJ-ALPHA-002', 'Concrete Foundation Mix', 'Alpha Construction Project', 'draft', 'River Sand Fine', 'River Sand Fine', '0.5', 'Cubic Meter'],
        ['IND/PROJ-ALPHA-002', 'Concrete Foundation Mix', 'Alpha Construction Project', 'draft', 'Aggregate 20mm', 'Aggregate 20mm', '0.8', 'Cubic Meter'],
        ['IND/PROJ-ALPHA-002', 'Concrete Foundation Mix', 'Alpha Construction Project', 'draft', 'Water', 'Water', '200', 'Liters'],
        
        # Project Flow Examples - Electrical
        ['IND/PROJ-BETA-001', 'Electrical Panel Assembly', 'Beta Electrical Project', 'draft', 'Distribution Board 12-way', 'Distribution Board 12-way', '1', 'Units'],
        ['IND/PROJ-BETA-001', 'Electrical Panel Assembly', 'Beta Electrical Project', 'draft', 'MCB 32A Single Pole', 'MCB 32A Single Pole', '12', 'Units'],
        ['IND/PROJ-BETA-001', 'Electrical Panel Assembly', 'Beta Electrical Project', 'draft', 'Copper Wire 4mm²', 'Copper Wire 4mm²', '50', 'Meters'],
        ['IND/PROJ-BETA-001', 'Electrical Panel Assembly', 'Beta Electrical Project', 'draft', 'Cable Gland 20mm', 'Cable Gland 20mm', '8', 'Units'],
        
        # Spare Parts Flow Examples - Pump Maintenance
        ['IND/SPARE-PUMP-001', 'Pump Motor Assembly', '', 'draft', 'SKF Bearing 6308', 'SKF Bearing 6308', '2', 'Units'],
        ['IND/SPARE-PUMP-001', 'Pump Motor Assembly', '', 'draft', 'Mechanical Seal 40mm', 'Mechanical Seal 40mm', '1', 'Units'],
        ['IND/SPARE-PUMP-001', 'Pump Motor Assembly', '', 'draft', 'V-Belt B50', 'V-Belt B50', '1', 'Units'],
        ['IND/SPARE-PUMP-001', 'Pump Motor Assembly', '', 'draft', 'Lithium Grease 400g', 'Lithium Grease 400g', '2', 'Units'],
        
        # Spare Parts Flow Examples - Conveyor Maintenance
        ['IND/SPARE-CONV-001', 'Conveyor Belt System', '', 'draft', 'Conveyor Belt 1200mm', 'Conveyor Belt 1200mm', '10', 'Meters'],
        ['IND/SPARE-CONV-001', 'Conveyor Belt System', '', 'draft', 'Belt Fastener Clips', 'Belt Fastener Clips', '20', 'Units'],
        ['IND/SPARE-CONV-001', 'Conveyor Belt System', '', 'draft', 'Roller Bearing 6205', 'Roller Bearing 6205', '8', 'Units'],
        ['IND/SPARE-CONV-001', 'Conveyor Belt System', '', 'draft', 'Drive Chain 16B-1', 'Drive Chain 16B-1', '5', 'Meters'],
        
        # Spare Parts Flow Examples - HVAC Maintenance
        ['IND/SPARE-HVAC-001', 'HVAC Unit Maintenance', '', 'draft', 'Air Filter 600x300', 'Air Filter 600x300', '4', 'Units'],
        ['IND/SPARE-HVAC-001', 'HVAC Unit Maintenance', '', 'draft', 'Fan Belt A38', 'Fan Belt A38', '2', 'Units'],
        ['IND/SPARE-HVAC-001', 'HVAC Unit Maintenance', '', 'draft', 'Refrigerant R410A', 'Refrigerant R410A', '2', 'Kg'],
        ['IND/SPARE-HVAC-001', 'HVAC Unit Maintenance', '', 'draft', 'Thermostat Digital', 'Thermostat Digital', '1', 'Units']
    ]
    
    # Simple user-friendly template
    simple_data = [
        # Headers
        ['Product Name', 'Project Name', 'Component Name', 'Quantity', 'Unit', 'Flow Type', 'Indent Reference', 'Status'],
        
        # Project Examples
        ['Steel Structure Assembly', 'Alpha Construction Project', 'Steel Rod 12mm', '50', 'Units', 'project', 'IND/PROJ-ALPHA-001', 'draft'],
        ['Steel Structure Assembly', 'Alpha Construction Project', 'Steel Plate 10mm', '20', 'Units', 'project', 'IND/PROJ-ALPHA-001', 'draft'],
        ['Concrete Foundation Mix', 'Alpha Construction Project', 'Portland Cement 50kg', '15', 'Bags', 'project', 'IND/PROJ-ALPHA-002', 'draft'],
        ['Electrical Panel Assembly', 'Beta Electrical Project', 'Distribution Board 12-way', '1', 'Units', 'project', 'IND/PROJ-BETA-001', 'draft'],
        
        # Spare Parts Examples (Project Name empty)
        ['Pump Motor Assembly', '', 'SKF Bearing 6308', '2', 'Units', 'spare', 'IND/SPARE-PUMP-001', 'draft'],
        ['Pump Motor Assembly', '', 'Mechanical Seal 40mm', '1', 'Units', 'spare', 'IND/SPARE-PUMP-001', 'draft'],
        ['Conveyor Belt System', '', 'Conveyor Belt 1200mm', '10', 'Meters', 'spare', 'IND/SPARE-CONV-001', 'draft'],
        ['HVAC Unit Maintenance', '', 'Air Filter 600x300', '4', 'Units', 'spare', 'IND/SPARE-HVAC-001', 'draft']
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
    
    # Create instructions file
    instructions = """
# Material Indent Unified Import Template

## Files Created:
1. Material_Indent_Unified_Import.csv - Ready-to-import format for Odoo
2. Material_Indent_Simple_Format.csv - User-friendly format for data preparation

## Template Structure:
Based on BOM format: Product | Quantity | BoM Type | Unit | BoM Lines/Component | BoM Lines/Quantity

## Key Features:
- Single file contains both PROJECT and SPARE PARTS examples
- Project flow: Includes project name, custom BOM names allowed
- Spare parts flow: Empty project name, exact name matching required
- Real-world examples: Construction, electrical, maintenance scenarios

## How to Use:

### For Direct Import (Material_Indent_Unified_Import.csv):
1. Replace sample data with your actual data
2. Ensure all BOMs and products exist in Odoo
3. Import directly using Odoo's import wizard

### For Data Preparation (Material_Indent_Simple_Format.csv):
1. Use this for easier data entry
2. Convert to import format when ready
3. Map columns during Odoo import process

## Flow Types:
- PROJECT: Custom BOM names, requires project reference
- SPARE: Exact name matching, no project reference needed

## Column Mapping:
- name = Indent Reference (unique identifier)
- bom_id = Product/BOM Name
- project_id = Project Name (empty for spare parts)
- state = Status (draft/submitted/approved/cancel)
- indent_line_ids/* = Component details (product, quantity, unit)

## Examples Included:
✓ Construction materials (steel, concrete, electrical)
✓ Maintenance spares (pumps, conveyors, HVAC)
✓ Both project-based and spare parts workflows
✓ Various units of measure (Units, Kg, Liters, Meters, etc.)

## Before Import:
1. Create all BOMs in MRP module
2. Set up all component products in Inventory
3. Create projects for project-flow indents
4. Configure units of measure

## Import Process:
1. Go to Material Indent → Indents
2. Click Favorites → Import Records
3. Upload CSV file
4. Map columns if needed
5. Test with few records first
6. Import all data

## Troubleshooting:
- "BOM not found": Create BOM first
- "Product not found": Add product to inventory
- "Project not found": Create project (for project flow)
- "Invalid quantity": Use positive decimal numbers
- "UoM not found": Configure unit of measure

Ready to import? Use Material_Indent_Unified_Import.csv directly!
"""
    
    with open('Unified_Import_Instructions.txt', 'w') as f:
        f.write(instructions)
    
    print("Created: Unified_Import_Instructions.txt")
    print("\n✅ Unified Material Indent templates created successfully!")
    print("\n📋 What you got:")
    print("   • Single CSV with project + spare parts examples")
    print("   • User-friendly format for data preparation") 
    print("   • Import-ready format for Odoo")
    print("   • Comprehensive instructions")
    print("\n🚀 Ready to import material indents with both project and spare parts workflows!")

if __name__ == "__main__":
    create_unified_template()