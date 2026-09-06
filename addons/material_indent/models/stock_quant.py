# -*- coding: utf-8 -*-
from collections import defaultdict
from odoo import api, fields, models, _
from odoo.osv import expression


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    reserved_used_by = fields.Char(
        string='Used By',
        compute='_compute_reserved_used_by',
        search='_search_reserved_used_by',
        help='Documents/Transfers/Manufacturing Orders currently reserving this stock',
        store=False,
    )

    @api.depends('reserved_quantity', 'location_id', 'product_id', 'lot_id', 'package_id', 'owner_id')
    def _compute_reserved_used_by(self):
        """Compute the human-readable summary of documents reserving stock for each quant."""
        reserved_quants = self.filtered(
            lambda q: q.reserved_quantity > 0 and q.location_id.usage in ('internal', 'transit')
        )
        (self - reserved_quants).reserved_used_by = False
        if not reserved_quants:
            return

        move_lines = self.env['stock.move.line'].search([
            ('product_id', 'in', reserved_quants.product_id.ids),
            ('location_id', 'in', reserved_quants.location_id.ids),
            ('state', 'not in', ('done', 'cancel', 'draft')),
            ('quantity', '>', 0),
        ])

        # Map by (product_id, location_id, lot_id, package_id, owner_id) -> (doc_name, origin, uom_name) -> qty
        ml_map = defaultdict(lambda: defaultdict(float))
        for ml in move_lines:
            key = (
                ml.product_id.id,
                ml.location_id.id,
                ml.lot_id.id if ml.lot_id else False,
                ml.package_id.id if ml.package_id else False,
                ml.owner_id.id if ml.owner_id else False,
            )

            # Determine source document name
            doc_name = (
                ml.move_id.picking_id.name or
                ml.move_id.raw_material_production_id.name or
                ml.move_id.production_id.name or
                ml.move_id.reference or
                ml.origin or
                _('Stock Move')
            )

            origin = (
                ml.move_id.picking_id.origin or
                ml.move_id.raw_material_production_id.origin or
                (ml.origin if ml.origin and ml.origin != doc_name else '') or
                ''
            )

            uom_name = ml.product_uom_id.name or ml.product_id.uom_id.name or ''
            doc_key = (doc_name, origin, uom_name)
            ml_map[key][doc_key] += ml.quantity

        for q in reserved_quants:
            key = (
                q.product_id.id,
                q.location_id.id,
                q.lot_id.id if q.lot_id else False,
                q.package_id.id if q.package_id else False,
                q.owner_id.id if q.owner_id else False,
            )
            doc_dict = ml_map.get(key, {})
            blocks = []
            for (doc_name, origin, uom_name), qty in doc_dict.items():
                origin_info = f' [{origin}]' if origin and origin != doc_name else ''
                qty_str = f'{qty:g} {uom_name}'.strip()
                blocks.append(f'{doc_name}{origin_info} ({qty_str})')

            q.reserved_used_by = ', '.join(blocks) if blocks else _('Reserved')

    def _search_reserved_used_by(self, operator, value):
        """Allow searching quants by reserving document name or origin."""
        if operator not in ('=', '!=', 'like', 'ilike', '=like', '=ilike', 'in', 'not in'):
            return []

        domain = [
            ('state', 'not in', ('done', 'cancel', 'draft')),
            ('quantity', '>', 0),
            '|', '|', '|',
            ('picking_id.name', operator, value),
            ('picking_id.origin', operator, value),
            ('move_id.raw_material_production_id.name', operator, value),
            ('move_id.raw_material_production_id.origin', operator, value),
        ]
        move_lines = self.env['stock.move.line'].search(domain)
        if not move_lines:
            return [('id', '=', 0)] if operator not in ('!=', 'not in') else []

        quant_domains = []
        for ml in move_lines:
            d = [
                ('product_id', '=', ml.product_id.id),
                ('location_id', '=', ml.location_id.id),
                ('reserved_quantity', '>', 0),
            ]
            if ml.lot_id:
                d.append(('lot_id', '=', ml.lot_id.id))
            if ml.package_id:
                d.append(('package_id', '=', ml.package_id.id))
            if ml.owner_id:
                d.append(('owner_id', '=', ml.owner_id.id))
            quant_domains.append(d)

        if quant_domains:
            combined = expression.OR(quant_domains)
            quants = self.search(combined)
            return [('id', 'in', quants.ids)]
        return [('id', '=', 0)]
