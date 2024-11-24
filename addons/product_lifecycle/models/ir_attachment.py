# -*- coding: utf-8 -*-
from odoo import models, fields

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    document_type = fields.Selection([
        ('drawing', 'Drawing'),
        ('specification', 'Specification'),
        ('test_report', 'Test Report'),
        ('manual', 'Manual'),
        ('certificate', 'Certificate'),
        ('other', 'Other')
    ], string='Document Type')