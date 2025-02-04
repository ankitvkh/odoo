from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_in_gst_composition = fields.Boolean(
        string='GST Composition Scheme',
        default=False,
        help='Enable if the company is registered under GST Composition Scheme'
    )