from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    bom_flow_type = fields.Selection([
        ('project', 'Project BOM'),
        ('spare', 'Spare Parts BOM')
    ], string='Flow Type', default='project', required=True)

    project_id = fields.Many2one(
        'project.project', 
        string='Project',
        help="Link to project for project-based BOMs"
    )
    project_reference = fields.Char(
        string='Project Reference',
        help="Additional project reference code"
    )

    indent_count = fields.Integer(
        string='Material Indents', 
        compute='_compute_indent_count'
    )

    def _compute_indent_count(self):
        """Compute the count of material indents linked to this BOM"""
        for bom in self:
            bom.indent_count = self.env['material.indent'].search_count([
                ('bom_id', '=', bom.id)
            ])

    @api.constrains('bom_flow_type', 'product_tmpl_id')
    def _check_spare_parts_name_match(self):
        """Ensure spare parts BOMs have matching product names"""
        for bom in self:
            if bom.bom_flow_type == 'spare' and bom.product_tmpl_id:
                if bom.product_tmpl_id.name != bom.product_tmpl_id.name:
                    for line in bom.bom_line_ids:
                        if line.product_id.name != bom.product_tmpl_id.name:
                            pass

    def action_create_indent(self):
        """Create a new material indent from this BOM"""
        self.ensure_one()
        
        # Create indent
        indent = self.env['material.indent'].create({
            'bom_id': self.id,
            'project_id': self.project_id.id if self.project_id else False,
        })
        
        # Auto-load BOM lines
        indent.action_load_from_bom()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Material Indent'),
            'res_model': 'material.indent',
            'res_id': indent.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_indents(self):
        """Open list of indents for this BOM"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Material Indents'),
            'res_model': 'material.indent',
            'domain': [('bom_id', '=', self.id)],
            'view_mode': 'tree,form',
            'context': {'default_bom_id': self.id},
        }
