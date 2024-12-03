# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    drawing_attachment_ids = fields.Many2many(
        'ir.attachment',
        'mrp_bom_drawing_rel',
        'bom_id',
        'attachment_id',
        string='Technical Drawings',
        help='Attach technical drawings related to this BOM'
    )