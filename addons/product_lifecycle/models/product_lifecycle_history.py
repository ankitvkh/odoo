# models/product_lifecycle_history.py
from odoo import models, fields, api


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

    previous_stage_id = fields.Many2one(
        'product.lifecycle.stage',
        string='Previous Stage'
    )

    date = fields.Datetime(
        string='Date',
        default=fields.Datetime.now,
        required=True
    )

    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
        required=True
    )

    notes = fields.Text('Notes')

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    # Add method to ensure company consistency
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'company_id' not in vals and 'lifecycle_id' in vals:
                lifecycle = self.env['product.lifecycle'].browse(vals['lifecycle_id'])
                vals['company_id'] = lifecycle.company_id.id
        return super().create(vals_list)

    def name_get(self):
        result = []
        for record in self:
            date_str = fields.Datetime.to_string(record.date)
            name = f"{record.lifecycle_id.name} - {record.stage_id.name} ({date_str})"
            result.append((record.id, name))
        return result