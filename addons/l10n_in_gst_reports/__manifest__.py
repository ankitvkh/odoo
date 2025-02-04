{
    'name': 'Indian GST Reports',
    'countries': ["in"],
    'version': '18.0.1.0.0',
    'category': 'Accounting/Localization/Reporting',
    'summary': 'GST Reports for Indian Localization',
    'description': """
        Generate GSTR-1 and GSTR-3B reports in Odoo 18 Community Edition.
        Features:
        * GSTR-1 Report Generation
        * GSTR-3B Report Generation
        * JSON Export for GST Portal
        * HSN Summary Report
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'account',
        'l10n_in',
    ],
    'data': [
        'security/gst_report_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/res_config_settings_views.xml',
        'views/gst_report_views.xml',
        'wizard/gst_report_wizard_views.xml',
        'report/gst_report_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'l10n_in_gst_reports/static/src/js/gst_report_handler.js',
            'l10n_in_gst_reports/static/src/xml/gst_report_templates.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}