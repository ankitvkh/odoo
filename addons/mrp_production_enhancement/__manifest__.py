# -*- coding: utf-8 -*-
{
    'name': 'Manufacturing Order Component Serial Numbers',
    'version': '1.0.0',
    'category': 'Manufacturing/Manufacturing',
    'summary': 'Add sequential serial numbers to Manufacturing Order raw material components list view',
    'description': """
        This module adds a sequential line number column (Sr. No.) to the raw material components list view on the Manufacturing Order form.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'mrp',
        'stock',
    ],
    'data': [
        'views/mrp_production_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
