# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    location_id = fields.Many2one(
        'location.master',
        string='Location',
        help='Location for this purchase order',
        index=True,
        default=lambda self: self.env.user.location_id.id if self.env.user.location_id else False
    )
    
    @api.onchange('user_id')
    def _onchange_user_id_location(self):
        """Set location based on buyer's location"""
        if self.user_id and self.user_id.location_id:
            self.location_id = self.user_id.location_id
