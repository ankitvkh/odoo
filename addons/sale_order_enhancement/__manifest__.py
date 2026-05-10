# -*- coding: utf-8 -*-
{
    'name': 'Sale Order Enhancement',
    'version': '1.0.0',
    'category': 'Sales',
    'summary': 'Enhanced Sale Order Lines and Optional Products with Taxes and Amount',
    'description': """
        Sale Order Enhancement
        ======================
        
        Enhances the Sale Order form to provide consistent experience:
        * Order Lines tab shows Taxes and Amount columns
        * Optional Products tab shows Taxes and Amount columns
        * Both tabs have options to add sections, notes, and catalog items
        * Improved user interface for better data entry
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'sale',
        'sale_management',
        'account',
        'material_indent',
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'data/res_company_data.xml',
        'views/sale_order_views.xml',
        'views/sale_report_templates.xml',
        'views/invoice_report_templates.xml',
        'views/sale_portal_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
