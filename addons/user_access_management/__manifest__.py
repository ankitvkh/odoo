# -*- coding: utf-8 -*-
{
    'name': 'User Access Management',
    'version': '1.0.0',
    'category': 'Administration',
    'summary': 'Comprehensive user access management with location-based security',
    'description': """
        User Access Management Module
        ==============================
        
        This module provides:
        * Location-based access control
        * Enhanced security group management
        * Record-level security (RLS)
        * Department and user linking
        * Comprehensive audit logging
        * Access rights matrix view
        * Bulk user operations
        
        Features:
        ---------
        - Location Master for organizational hierarchy
        - Extended user model with location and department fields
        - Location-based record filtering
        - Module-level access control
        - Security audit trail
        - User import and bulk operations
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'hr',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/location_master_views.xml',
        'views/res_users_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
