{
    'name': 'Enhanced Delete with Confirmation',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Enhanced delete functionality with confirmation dialogs for linked records',
    'description': """
        This module enhances the delete functionality in Odoo by showing confirmation dialogs
        when attempting to delete records that have linked data. Users can choose to:
        - Cancel the deletion
        - Delete only the selected record (unlink relationships)
        - Cascade delete all linked records
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/enhanced_delete_views.xml',
        'views/enhanced_delete_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'enhanced_delete/static/src/js/enhanced_delete.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}