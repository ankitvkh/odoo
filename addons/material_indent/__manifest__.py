{
    "name": "Material Indent",
    "version": "17.0.1.0.0",
    "summary": "Dual-flow material requisition: project & spare parts",
    "description": "Material indent module that supports project-based BOMs with custom names and spare-parts BOMs that must match product names. Auto-generates indents and POs from BOMs.",
    "category": "Inventory/Manufacturing",
    "author": "AnkitVKH",
    "website": "https://example.com",
    "license": "LGPL-3",
    "depends": [
        "mrp",
        "purchase",
        "stock",
        "project"
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence_data.xml",
        "views/mrp_bom_views.xml",
        "views/material_indent_views.xml"
    ],
    "demo": [
        "data/demo_data.xml"
    ],
    "installable": True,
    "application": False,
    "auto_install": False
}
