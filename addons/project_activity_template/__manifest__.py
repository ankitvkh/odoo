{
    'name': 'Project Activity Templates',
    'version': '18.0.1.0.0',  # Add version format
    'category': 'Project',
    'summary': 'Create and apply task templates to projects',
    'sequence': 10,
    'description': """
        This module allows you to create templates for project activities
        and apply them to projects in bulk.
    """,
    'author': 'Ankit K',
    'depends': ['project', 'mail'],
    'data': [
        'security/project_template_security.xml',
        'security/ir.model.access.csv',
        'views/project_template_views.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3'
}