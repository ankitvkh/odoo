# -*- coding: utf-8 -*-
{
    'name': 'Enhanced Delete Confirmation',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'summary': 'Enhanced delete with unlink or cascade options',
    'description': """
Enhanced Delete Confirmation
============================

Features:
---------
* Shows confirmation dialog when deleting records
* Detects linked records across the database
* Two delete modes:
  - Unlink Only: Removes relationships and deletes only selected records
  - Cascade Delete: Deletes selected records AND all linked data
* Works on all models (configurable exclusions)
* Prevents accidental data loss

Configuration:
--------------
Configure via Settings > General Settings > Enhanced Delete Confirmation
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/enhanced_delete_views.xml',
        'views/res_config_settings_views.xml',
        'data/default_settings.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'enhanced_delete_confirm/static/src/js/enhanced_delete.esm.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}