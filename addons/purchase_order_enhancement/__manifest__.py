# -*- coding: utf-8 -*-
{
    'name': 'Purchase Order Enhancement',
    'version': '1.0.0',
    'category': 'Purchase',
    'summary': 'Custom Purchase Order Sequence Format',
    'description': """
        Purchase Order Enhancement
        ==========================
        
        Implements custom purchase order sequence format:
        PA/ORDER/QTN-YY-YY/NNNN
        
        Where:
        - PA: Fixed prefix
        - ORDER: Fixed text
        - QTN-YY-YY: Financial year (e.g., 25-26)
        - NNNN: 4-digit sequence number
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'purchase',
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'views/purchase_report_templates.xml',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
