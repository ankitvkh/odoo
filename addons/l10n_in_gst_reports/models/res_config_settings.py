from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_in_gst_report_dir = fields.Char(
        string='GST Report Directory',
        config_parameter='l10n_in_gst_reports.report_directory',
        help='Directory to store generated GST report files'
    )

    l10n_in_gst_validation_method = fields.Selection([
        ('basic', 'Basic'),
        ('detailed', 'Detailed'),
        ('strict', 'Strict')
    ],
        config_parameter='l10n_in_gst_reports.validation_method',
        default='basic',
        string='Validation Method',
        required=True
    )

    l10n_in_gst_auto_validate = fields.Boolean(
        config_parameter='l10n_in_gst_reports.auto_validate',
        default=True,
        string='Auto-validate GST Data'
    )

    l10n_in_gst_hsn_mandatory = fields.Boolean(
        config_parameter='l10n_in_gst_reports.hsn_mandatory',
        default=True,
        string='Mandatory HSN Code'
    )

    l10n_in_gst_composition = fields.Boolean(
        related='company_id.l10n_in_gst_composition',
        readonly=False,
        string='GST Composition Scheme'
    )

    def set_values(self):
        super().set_values()
        # Additional configuration logic if needed
        if self.l10n_in_gst_hsn_mandatory:
            # Update product template form view to make HSN code required
            self.env['ir.ui.view'].search([
                ('model', '=', 'product.template'),
                ('inherit_id', '!=', False)
            ]).write({'active': True})

    @api.model
    def get_values(self):
        res = super().get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()

        res.update(
            l10n_in_gst_report_dir=ICPSudo.get_param('l10n_in_gst_reports.report_directory'),
            l10n_in_gst_validation_method=ICPSudo.get_param('l10n_in_gst_reports.validation_method', 'basic'),
            l10n_in_gst_auto_validate=ICPSudo.get_param('l10n_in_gst_reports.auto_validate', True),
            l10n_in_gst_hsn_mandatory=ICPSudo.get_param('l10n_in_gst_reports.hsn_mandatory', True)
        )
        return res