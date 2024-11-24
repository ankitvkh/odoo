{
    'name': 'Product Lifecycle Management',
    'version': '18.0.1.0.0',
    'category': 'Manufacturing/Product Lifecycle',
    'summary': 'Manage product lifecycle stages from conception to retirement',
    'description': """
Product Lifecycle Management
===========================
This module enables:
- Product lifecycle stage tracking
- Document management per stage
- Stage transition controls
- Full history tracking
- Approval workflows
""",
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'product',
        'mail',
    ],
    'data': [
        'security/product_lifecycle_security.xml',
        'security/ir.model.access.csv',
        'data/product_lifecycle_sequence.xml',
        'views/product_lifecycle_stage_views.xml',
        'views/product_lifecycle_views.xml',
        'views/product_lifecycle_menus.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}