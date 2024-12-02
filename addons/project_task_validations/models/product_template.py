from odoo import models, fields, api
from odoo.tools.translate import _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    preferred_vendor_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='product_preferred_vendor_rel',
        column1='product_id',
        column2='partner_id',
        string='Preferred Vendors',
        domain="[('is_company', '=', True), ('supplier_rank', '>', 0)]",
        check_company=True,
        help=_("Select vendors that are preferred for this product")
    )