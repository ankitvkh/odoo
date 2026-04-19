from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    user_id = fields.Many2one(
        'res.users', 
        string='Designated Person',
        index=True, 
        tracking=True,
        default=lambda self: self.env.user,
        domain="[('share', '=', False)]"
    )
