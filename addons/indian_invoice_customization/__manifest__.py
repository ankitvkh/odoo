# -*- coding: utf-8 -*-
{
    'name': 'Indian Invoice Customization',
    'version': '1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Customize invoices for Indian market with GST and INR',
    'description': """
        Indian Invoice Customization
        =============================
        
        This module customizes Odoo invoices for the Indian market:
        * Changes invoice name from "Proforma Invoice" to "Tax Invoice"
        * Sets default currency to Indian Rupees (INR)
        * Renames "Untaxed Amount" to "Basic Amount"
        * Renames "Tax" to "GST"
        * Creates default 18% GST tax
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'account',
        'sale',
    ],
    'data': [
        'data/account_tax_data.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
