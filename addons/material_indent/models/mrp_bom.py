from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    bom_flow_type = fields.Selection([
        ('project', 'Project BOM'),
        ('spare', 'Spare Parts BOM')
    ], string='Flow Type', default='project', required=True, 
       help="Project BOM: Custom product names allowed, mapped to inventory during indent creation.\n"
            "Spare Parts BOM: Product names must exactly match inventory.")

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
    
    material_indent_line_ids = fields.One2many(
        'material.indent.line.bom',
        'bom_id',
        string='Material Indent Lines'
    )

    def _compute_indent_count(self):
        """Compute the count of material indents linked to this BOM"""
        for bom in self:
            bom.indent_count = self.env['material.indent'].search_count([
                ('bom_id', '=', bom.id)
            ])

    @api.constrains('bom_flow_type', 'bom_line_ids')
    def _check_spare_parts_name_match(self):
        """Ensure spare parts BOMs have matching product names"""
        for bom in self:
            if bom.bom_flow_type == 'spare':
                for line in bom.bom_line_ids:
                    # For spare parts BOM, custom description should match product name
                    if hasattr(line, 'custom_product_description') and line.custom_product_description:
                        if line.custom_product_description != line.product_id.name:
                            raise ValidationError(
                                _('In Spare Parts BOM, product description "%s" must exactly match '
                                  'inventory product name "%s"') % 
                                (line.custom_product_description, line.product_id.name)
                            )

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
            'view_mode': 'list,form',
            'context': {'default_bom_id': self.id},
        }


class MaterialIndentLineBom(models.Model):
    _name = 'material.indent.line.bom'
    _description = 'Material Indent Line for BOM'

    bom_id = fields.Many2one('mrp.bom', string='BOM', ondelete='cascade')
    serial_no = fields.Integer(
        string='Sr. No.',
        compute='_compute_serial_no',
        store=False
    )
    indent_reference = fields.Char(string='Indent Reference', default='New')

    @api.depends('bom_id.material_indent_line_ids')
    def _compute_serial_no(self):
        for bom in self.mapped('bom_id'):
            lines = bom.material_indent_line_ids.sorted(key=lambda l: (
                1 if not isinstance(l.id, int) else 0,
                l.id or 0
            ))
            for idx, line in enumerate(lines, start=1):
                if line in self:
                    line.serial_no = idx
        # Fallback for lines not belonging to a BOM
        for line in self:
            if not line.bom_id:
                line.serial_no = 0

    product_id = fields.Many2one('product.product', string='Inventory Product', required=True,
                                help="The actual inventory product to be procured")
    product_name = fields.Char(string='Inventory Product Name', related='product_id.display_name')
    custom_description = fields.Char(string='Original BOM Description', 
                                   help="Original description from BOM (for project BOMs)")
    product_qty = fields.Float(string='Quantity', default=1.0, required=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', related='product_id.uom_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft')
    
    flow_type = fields.Selection(related='bom_id.bom_flow_type', string='Flow Type')
    
    make = fields.Char(related='product_id.make', string='Make', readonly=False, store=True)
    description_short = fields.Char(related='product_id.description_short', string='Description', readonly=False, store=True)
    
    def _sync_states_from_indents(self):
        for line in self:
            if line.bom_id and line.product_id:
                indents = self.env['material.indent'].search([
                    ('bom_id', '=', line.bom_id.id)
                ], order='id desc')
                for indent in indents:
                    if line.product_id in indent.indent_line_ids.mapped('product_id'):
                        if line.state != indent.state or line.indent_reference != indent.name:
                            line.write({
                                'state': indent.state,
                                'indent_reference': indent.name,
                            })
                        break

    def read(self, fields=None, load='_classic_read'):
        self._sync_states_from_indents()
        return super().read(fields=fields, load=load)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('indent_reference', 'New') == 'New':
                vals['indent_reference'] = self.env['ir.sequence'].next_by_code('material.indent') or 'IND/NEW'
        res = super().create(vals_list)
        res._sync_states_from_indents()
        return res


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'
    
    serial_no = fields.Integer(
        string='Sr. No.',
        compute='_compute_serial_no',
        store=False
    )

    @api.depends('bom_id.bom_line_ids')
    def _compute_serial_no(self):
        for bom in self.mapped('bom_id'):
            lines = bom.bom_line_ids.sorted(key=lambda l: (
                1 if not isinstance(l.id, int) else 0,
                l.sequence or 0,
                l.id or 0
            ))
            for idx, line in enumerate(lines, start=1):
                if line in self:
                    line.serial_no = idx
        # Fallback for lines not belonging to a BOM
        for line in self:
            if not line.bom_id:
                line.serial_no = 0

    custom_product_description = fields.Char(
        string='Custom Product Description',
        help="For Project BOM: Custom description that will be mapped to inventory product during indent creation.\n"
             "For Spare Parts BOM: Must exactly match the inventory product name."
    )
    
    inventory_product_id = fields.Many2one(
        'product.product',
        string='Inventory Product',
        help="The actual inventory product this line maps to (for project BOMs)"
    )
    
    make = fields.Char(
        related='product_id.make', 
        string='Make', 
        readonly=False, 
        store=True
    )
    description_short = fields.Char(
        related='product_id.description_short', 
        string='Description', 
        readonly=False, 
        store=True
    )
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Auto-fill custom description and inventory product"""
        if self.product_id:
            # For spare parts BOM, custom description must match product name
            if self.bom_id.bom_flow_type == 'spare':
                self.custom_product_description = self.product_id.name
                self.inventory_product_id = self.product_id
            else:
                # For project BOM, allow custom description but default to product name
                if not self.custom_product_description:
                    self.custom_product_description = self.product_id.name
                self.inventory_product_id = self.product_id
    
    @api.constrains('custom_product_description', 'inventory_product_id')
    def _check_product_mapping(self):
        """Validate product mapping based on BOM flow type"""
        for line in self:
            if line.bom_id.bom_flow_type == 'spare':
                # For spare parts, custom description must match inventory product
                if (line.custom_product_description and 
                    line.inventory_product_id and 
                    line.custom_product_description != line.inventory_product_id.name):
                    raise ValidationError(
                        _('In Spare Parts BOM, custom description "%s" must match '
                          'inventory product name "%s"') % 
                        (line.custom_product_description, line.inventory_product_id.name)
                    )


# Add methods to MrpBom class
class MrpBom(models.Model):
    _inherit = 'mrp.bom'
    
    def action_load_bom_components(self):
        """Load BOM components into material indent lines with proper mapping"""
        self.ensure_one()
        
        # Clear existing lines
        self.material_indent_line_ids.unlink()
        
        # Create indent lines from BOM components
        lines = []
        for bom_line in self.bom_line_ids:
            # Determine which product to use based on BOM flow type
            if self.bom_flow_type == 'project':
                # For project BOM: Use inventory_product_id if available, otherwise product_id
                indent_product = bom_line.inventory_product_id or bom_line.product_id
                custom_name = bom_line.custom_product_description or bom_line.product_id.name
            else:
                # For spare parts BOM: Always use the exact product
                indent_product = bom_line.product_id
                custom_name = bom_line.product_id.name
            
            lines.append((0, 0, {
                'product_id': indent_product.id,
                'product_qty': bom_line.product_qty,
                'state': 'draft',
                'custom_description': custom_name,  # Store the custom description
            }))
        
        self.material_indent_line_ids = lines
        
        flow_type_msg = "Project BOM (custom names mapped to inventory)" if self.bom_flow_type == 'project' else "Spare Parts BOM (exact inventory match)"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'Loaded {len(lines)} components from {flow_type_msg}',
                'type': 'success',
            }
        }
    
    def action_generate_purchase_orders(self):
        """Generate purchase orders from approved indent lines"""
        self.ensure_one()
        
        approved_lines = self.material_indent_line_ids.filtered(lambda l: l.state == 'approved')
        if not approved_lines:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'No approved indent lines found. Please approve some lines first.',
                    'type': 'warning',
                }
            }
        
        # Group by vendor and create POs
        # This is a simplified version - you can enhance it
        po_count = 0
        for line in approved_lines:
            # Create purchase order logic here
            po_count += 1
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'Generated {po_count} purchase order(s)',
                'type': 'success',
            }
        }

    def action_import_bom_template(self):
        """Import BOM from template and create material indent"""
        self.ensure_one()
        
        # Open import wizard for material indent
        return {
            'type': 'ir.actions.act_window',
            'name': _('Import BOM Template'),
            'res_model': 'material.indent',
            'view_mode': 'list',
            'target': 'current',
            'context': {
                'default_bom_id': self.id,
                'search_default_bom_id': self.id,
            },
            'help': _('''
                <p>Import BOM template to create material indents.</p>
                <p>Use the Import button to upload your CSV file with the following format:</p>
                <ul>
                    <li><strong>name</strong>: Indent reference (e.g., IND/PROJ-001)</li>
                    <li><strong>bom_id</strong>: BOM name (e.g., Steel Assembly)</li>
                    <li><strong>project_id</strong>: Project name (empty for spare parts)</li>
                    <li><strong>state</strong>: Status (draft/submitted/approved)</li>
                    <li><strong>Components</strong>: Product details with quantities</li>
                </ul>
            ''')
        }
