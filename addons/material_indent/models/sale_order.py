from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    user_id = fields.Many2one(string='Designated Person')

