# -*- coding: utf-8 -*-
{
    'name': 'Manufacturing BOM Import',
    'version': '18.0.1.0.0',
    'category': 'Manufacturing/Manufacturing',
    'summary': 'Import BOMs from spreadsheet and attach drawings',
    'description': """
        This module allows you to:
        * Import Bills of Materials (BOMs) from CSV files
        * Attach technical drawings to BOMs
        * Automatically create products if they don't exist
        * Validate data during import
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'mrp'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/bom_import_views.xml',
        'views/mrp_bom_views.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'sequence': 100,
    'assets': {}
}