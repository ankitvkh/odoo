# -*- coding: utf-8 -*-
{
    'name': 'Project Enhancement',
    'version': '1.0.0',
    'category': 'Services/Project',
    'summary': 'Custom configurations for projects (disables project name translations)',
    'description': """
        Project Enhancement
        ====================
        
        This module provides core fixes to Odoo projects to address synchronization issues between different translation locales, specifically concerning project duplication.
        
        Features:
        ---------
        * Disables dynamic translation on internal project names.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'project',
        'project_activity_template',
    ],
    'data': [
        'security/project_security.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
