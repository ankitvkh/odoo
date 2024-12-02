{
    'name': 'Project Task Validations',
    'version': '18.0.1.0.0',
    'category': 'Project',
    'summary': 'Adds additional validations to project tasks',
    'description': """
        Enhances project tasks with:
        - Strict dependency enforcement
        - Document upload requirement validation
    """,
    'depends': ['project',
                'base',
                'product',
                'purchase'],
    'data': [
        'security/project_security.xml',
        'data/cron_data.xml',
        'views/project_views.xml',
        'views/product_template_views.xml',
        'views/purchase_order_views.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}