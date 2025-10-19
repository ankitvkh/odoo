from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    bom_flow_type = fields.Selection([
        ('project', 'Project BOM'),
        ('spare', 'Spare Parts BOM')
    ], string='Flow Type', default='project', required=True)

    project_id = fields.Many2one('project.project', string='Project')
    project_reference = fields.Char(string='Project Reference')

    indent_count = fields.Integer(string='Material Indents', compute='_compute_indent_count')

    @api.depends('name')
    def _compute_indent_count(self):
        indent_obj = self.env['material.indent']
        for bom in self:
            domain = [('bom_id', '=', bom.id)]
            bom.indent_count = indent_obj.search_count(domain)
