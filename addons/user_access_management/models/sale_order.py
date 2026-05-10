# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    location_id = fields.Many2one(
        'location.master',
        string='Location',
        help='Location for this sales order',
        index=True,
        default=lambda self: self.env.user.location_id.id if self.env.user.location_id else False
    )
