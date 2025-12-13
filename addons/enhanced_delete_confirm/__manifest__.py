{
    'name': 'Enhanced Delete Confirmation',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Enhanced delete functionality with confirmation dialogs',
    'description': 'Shows confirmation dialogs when deleting records with linked data',
    'author': 'Your Company',
    'depends': ['base', 'web'],
    'data': [
        'views/enhanced_delete_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'enhanced_delete_confirm/static/src/js/enhanced_delete.js',
        ],
    },
    'installable': True,
    'application': False,
}