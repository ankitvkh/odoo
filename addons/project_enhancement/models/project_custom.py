# -*- coding: utf-8 -*-

from odoo import models, fields

class Project(models.Model):
    _inherit = 'project.project'
    
    name = fields.Char("Name", translate=False)
