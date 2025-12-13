# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enhanced_delete_enabled = fields.Boolean(
        string='Enable Enhanced Delete',
        default=True,
        config_parameter='enhanced_delete_confirm.enabled'
    )
    
    enhanced_delete_excluded_models = fields.Text(
        string='Excluded Models',
        help='Comma-separated list of models to exclude from enhanced delete. '
             'Example: ir.ui.menu,ir.model,ir.model.fields',
        config_parameter='enhanced_delete_confirm.excluded_models'
    )
    
    enhanced_delete_min_records = fields.Integer(
        string='Minimum Records for Confirmation',
        default=1,
        help='Show confirmation dialog only when deleting this many records or more',
        config_parameter='enhanced_delete_confirm.min_records'
    )