# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockLocation(models.Model):
    _inherit = 'stock.location'
    
    org_location_id = fields.Many2one(
        'location.master',
        string='Organization Location',
        help='Organization location for access control',
        index=True
    )


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    org_location_id = fields.Many2one(
        'location.master',
        string='Organization Location',
        help='Organization location for this stock move',
        compute='_compute_org_location',
        store=True,
        index=True
    )
    
    @api.depends('location_id', 'location_id.org_location_id')
    def _compute_org_location(self):
        """Compute organization location from stock location"""
        for move in self:
            move.org_location_id = move.location_id.org_location_id if move.location_id else False
