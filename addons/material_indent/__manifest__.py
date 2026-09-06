{
    'name': 'Material Indent',
    'version': '18.0.1.2.0',
    'summary': 'Dual-flow material requisition: project & spare parts',
    'description': '''
        Material indent module that supports project-based BOMs with custom names 
        and spare-parts BOMs that must match product names. 
        Auto-generates indents and POs from BOMs.
    ''',
    'category': 'Inventory/Manufacturing',
    'sequence': 165,
    'author': 'AnkitVKH',
    'website': 'https://example.com',
    'license': 'LGPL-3',
    'depends': [
        'mrp',
        'purchase',
        'stock',
        'project',
        'sale'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/mrp_bom_views.xml',
        'views/material_indent_views.xml',
        'views/product_template_views.xml',
        'views/purchase_order_views.xml',
        'views/sale_order_views.xml',
        'views/stock_quant_views.xml',
        'report/sale_report_templates.xml'
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'assets': {}
}
