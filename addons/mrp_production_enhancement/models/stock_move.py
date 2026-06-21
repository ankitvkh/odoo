# -*- coding: utf-8 -*-
from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    serial_no = fields.Integer(
        string='Sr. No.',
        compute='_compute_serial_no',
        store=False
    )

    @api.depends('raw_material_production_id.move_raw_ids')
    def _compute_serial_no(self):
        for production in self.mapped('raw_material_production_id'):
            # Sort moves using Odoo's visual hierarchy order, putting draft lines (NewId) at the end
            moves = production.move_raw_ids.sorted(key=lambda m: (
                1 if not isinstance(m.id, int) else 0,
                m.is_done,
                0 if m.manual_consumption else 1,
                m.sequence or 0,
                m.id or 0
            ))
            for idx, move in enumerate(moves, start=1):
                if move in self:
                    move.serial_no = idx
        # Fallback for moves not belonging to an MO
        for move in self:
            if not move.raw_material_production_id:
                move.serial_no = 0
