# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Project(models.Model):
    _inherit = 'project.project'
    
    name = fields.Char("Name", translate=False)
    privacy_visibility = fields.Selection(default='employees')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'privacy_visibility' not in vals:
                vals['privacy_visibility'] = 'employees'
        return super().create(vals_list)

    def copy(self, default=None):
        if default is None:
            default = {}
        # Ensure duplicated projects are visible to all internal users by default
        if 'privacy_visibility' not in default:
            default['privacy_visibility'] = 'employees'
        return super().copy(default)
