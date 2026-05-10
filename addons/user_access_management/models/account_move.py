# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    location_id = fields.Many2one(
        'location.master',
        string='Location',
        help='Location for this invoice/bill',
        index=True,
        compute='_compute_location_id',
        store=True,
        readonly=False
    )
    
    @api.depends('invoice_line_ids.sale_line_ids.order_id.location_id', 'invoice_line_ids.purchase_line_id.order_id.location_id')
    def _compute_location_id(self):
        """Compute location from linked sale/purchase orders"""
        for move in self:
            location = False
            # Check for sale orders
            sale_orders = move.invoice_line_ids.sale_line_ids.order_id
            if sale_orders:
                location = sale_orders[0].location_id
            
            # If not found, check for purchase orders
            if not location:
                purchase_orders = move.invoice_line_ids.purchase_line_id.order_id
                if purchase_orders:
                    location = purchase_orders[0].location_id
            
            # Fallback to user location if still not set and it's a new record
            if not location and not move.location_id:
                location = self.env.user.location_id
                
            move.location_id = location
