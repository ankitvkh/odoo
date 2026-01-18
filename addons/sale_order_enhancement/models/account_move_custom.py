# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    offer_type = fields.Selection([
        ('actual', 'Actual Offer'),
        ('technical', 'Technical Offer'),
        ('budgetary', 'Budgetary Offer'),
    ], string='Offer Type', compute='_compute_offer_type', store=True,
       help='Offer type linked to the source sales order')

    @api.depends('invoice_origin', 'invoice_line_ids.sale_line_ids.order_id.offer_type')
    def _compute_offer_type(self):
        for move in self:
            offer_type = 'actual'
            # Try to find linked sale order from invoice lines
            sale_orders = move.invoice_line_ids.sale_line_ids.order_id
            if sale_orders:
                # Use the offer type from the first linked SO (usually there's only one or they share properties)
                offer_type = sale_orders[0].offer_type
            
            move.offer_type = offer_type
