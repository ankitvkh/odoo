# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime

class ProductLifecycleHistory(models.Model):
    _name = 'product.lifecycle.history'
    _description = 'Product Lifecycle History'
    _order = 'date desc, id desc'

    lifecycle_id = fields.Many2one(
        'product.lifecycle',
        string='Lifecycle',
        required=True,
        ondelete='cascade'
    )
    stage_id = fields.Many2one(
        'product.lifecycle.stage',
        string='Stage',
        required=True
    )
    date = fields.Datetime(
        string='Date',
        required=True,
        default=fields.Datetime.now
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        default=lambda self: self.env.user
    )
    notes = fields.Text(
        string='Notes'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='lifecycle_id.company_id',
        store=True
    )

    @api.model
    def create(self, vals):
        # Add a note about who made the change
        if not vals.get('notes'):
            stage = self.env['product.lifecycle.stage'].browse(vals.get('stage_id'))
            user = self.env.user
            vals['notes'] = _('Stage changed to "%s" by %s') % (stage.name, user.name)
        return super(ProductLifecycleHistory, self).create(vals)