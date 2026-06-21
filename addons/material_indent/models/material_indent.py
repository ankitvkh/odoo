from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class MaterialIndent(models.Model):
    _name = 'material.indent'
    _description = 'Material Indent'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(
        string='Indent Reference', 
        required=True, 
        copy=False, 
        readonly=True, 
        default='New',
        tracking=True
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', readonly=True, tracking=True)

    bom_id = fields.Many2one(
        'mrp.bom', 
        string='BOM', 
        required=True,
        tracking=True
    )
    
    bom_flow_type = fields.Selection(
        related='bom_id.bom_flow_type',
        string='Flow Type',
        readonly=True
    )
    
    project_id = fields.Many2one(
        'project.project', 
        string='Project',
        tracking=True
    )
    
    indent_line_ids = fields.One2many(
        'material.indent.line', 
        'indent_id', 
        string='Indent Lines', 
        copy=True
    )
    
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.company,
        required=True
    )
    
    purchase_order_ids = fields.Many2many(
        'purchase.order',
        string='Purchase Orders',
        compute='_compute_purchase_orders',
        store=False
    )
    
    purchase_count = fields.Integer(
        string='PO Count',
        compute='_compute_purchase_orders'
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Generate sequence number on creation"""
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                seq = self.env.ref('material_indent.sequence_material_indent', raise_if_not_found=False)
                vals['name'] = seq.next_by_id() if seq else self.env['ir.sequence'].next_by_code('material.indent') or 'IND/NEW'
        records = super().create(vals_list)
        records._sync_bom_indent_lines()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._sync_bom_indent_lines()
        return res

    def unlink(self):
        # Delete related BOM indent lines when deleting the indent
        bom_lines = self.env['material.indent.line.bom'].search([
            ('indent_reference', 'in', self.mapped('name'))
        ])
        if bom_lines:
            bom_lines.unlink()
        return super().unlink()

    def _compute_purchase_orders(self):
        """Find related purchase orders by origin"""
        for indent in self:
            pos = self.env['purchase.order'].search([('origin', '=', indent.name)])
            indent.purchase_order_ids = pos
            indent.purchase_count = len(pos)

    def action_load_from_bom(self):
        """Load BOM components into indent lines"""
        self.ensure_one()
        
        if not self.bom_id:
            raise UserError(_('Please select a BOM first.'))
        
        bom = self.bom_id
        
        # Set project for project flow
        if bom.bom_flow_type == 'project' and bom.project_id:
            self.project_id = bom.project_id.id
        
        # Validate spare parts flow
        if bom.bom_flow_type == 'spare' and bom.product_tmpl_id:
            for line in bom.bom_line_ids:
                # For spare parts, we ensure product names are used correctly
                # The BOM product name becomes the reference
                pass  # Validation happens in BOM model
        
        # Clear existing lines and create new ones
        lines = []
        for line in bom.bom_line_ids:
            product = line.product_id
            
            # Check product availability
            available_qty = product.qty_available
            
            lines.append((0, 0, {
                'product_id': product.id,
                'product_name': product.display_name,  # Always use inventory product name
                'product_qty': line.product_qty,
                'uom_id': line.product_uom_id.id,
                'available_qty': available_qty,
            }))
        
        self.indent_line_ids = [(5, 0, 0)] + lines
        
        self.message_post(body=_('Loaded %d lines from BOM: %s') % (len(lines), bom.display_name))
        self._sync_bom_indent_lines()
        return True

    def _sync_bom_indent_lines(self):
        for rec in self:
            if not rec.bom_id:
                continue
            
            # Find existing BOM indent lines linked to this indent reference
            existing_bom_lines = self.env['material.indent.line.bom'].search([
                ('bom_id', '=', rec.bom_id.id),
                ('indent_reference', '=', rec.name)
            ])
            
            processed_products = set()
            for line in rec.indent_line_ids:
                if not line.product_id:
                    continue
                
                # Check if we already have a line for this product in this BOM/Indent combination
                bom_line = existing_bom_lines.filtered(lambda l: l.product_id == line.product_id)
                vals = {
                    'bom_id': rec.bom_id.id,
                    'indent_reference': rec.name,
                    'product_id': line.product_id.id,
                    'product_qty': line.product_qty,
                    'state': rec.state,
                    'custom_description': line.description_short or line.product_id.name,
                }
                
                if bom_line:
                    bom_line.write(vals)
                else:
                    self.env['material.indent.line.bom'].create(vals)
                
                processed_products.add(line.product_id.id)
            
            # Delete any existing BOM lines for products that were removed from this indent
            lines_to_delete = existing_bom_lines.filtered(lambda l: l.product_id.id not in processed_products)
            if lines_to_delete:
                lines_to_delete.unlink()

    def action_submit(self):
        """Submit indent for approval"""
        for rec in self:
            if not rec.indent_line_ids:
                raise ValidationError(_('Cannot submit an empty indent. Please load items from BOM first.'))
            rec.state = 'submitted'
            rec.message_post(body=_('Indent submitted for approval'))
            rec._sync_bom_indent_lines()

    def action_approve(self):
        """Approve indent and create purchase orders"""
        for rec in self:
            rec.state = 'approved'
            rec.message_post(body=_('Indent approved'))
            rec._sync_bom_indent_lines()
            rec._create_purchase_orders()

    def action_cancel(self):
        """Cancel the indent"""
        for rec in self:
            rec.state = 'cancel'
            rec.message_post(body=_('Indent cancelled'))
            rec._sync_bom_indent_lines()

    def action_reset_to_draft(self):
        """Reset to draft state"""
        for rec in self:
            rec.state = 'draft'
            rec.message_post(body=_('Indent reset to draft'))
            rec._sync_bom_indent_lines()

    def _create_purchase_orders(self):
        """Create purchase orders grouped by vendor"""
        self.ensure_one()
        
        PurchaseOrder = self.env['purchase.order']
        partner_map = {}
        
        # Group lines by vendor
        missing_vendor_products = []
        for line in self.indent_line_ids:
            sellers = line.product_id.seller_ids
            if not sellers:
                missing_vendor_products.append(line.product_id.display_name)
            else:
                partner = sellers[0].partner_id
                partner_map.setdefault(partner.id, []).append(line)
        
        if missing_vendor_products:
            raise UserError(_(
                "Cannot approve and create Purchase Orders. The following products do not have any vendor configured:\n\n%s\n\n"
                "Please configure a vendor on these products (under the Purchase tab) before proceeding."
            ) % "\n".join(f"- {p}" for p in missing_vendor_products))
        
        created_pos = []
        
        # Create PO for each vendor
        for partner_id, lines in partner_map.items():
            po_vals = {
                'partner_id': partner_id if partner_id else False,
                'company_id': self.company_id.id,
                'origin': self.name,
            }
            
            po = PurchaseOrder.create(po_vals)
            
            # Create PO lines
            for line in lines:
                price = 0.0
                if line.product_id.seller_ids:
                    price = line.product_id.seller_ids[0].price
                else:
                    price = line.product_id.standard_price
                
                po.order_line = [(0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_name,  # Use preserved product name
                    'product_qty': line.product_qty,
                    'product_uom': line.uom_id.id,
                    'price_unit': price,
                    'date_planned': fields.Datetime.now(),
                })]
            
            created_pos.append(po)
        
        self.message_post(
            body=_('Created %d Purchase Order(s)') % len(created_pos)
        )
        
        return created_pos

    def action_view_purchase_orders(self):
        """View related purchase orders"""
        self.ensure_one()
        
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        pos = self.env['purchase.order'].search([('origin', '=', self.name)])
        
        if len(pos) > 1:
            action['domain'] = [('id', 'in', pos.ids)]
        elif len(pos) == 1:
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            action['res_id'] = pos.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        
        return action


class MaterialIndentLine(models.Model):
    _name = 'material.indent.line'
    _description = 'Material Indent Line'

    indent_id = fields.Many2one(
        'material.indent', 
        string='Indent', 
        ondelete='cascade',
        required=True
    )
    serial_no = fields.Integer(
        string='Sr. No.',
        compute='_compute_serial_no',
        store=False
    )

    @api.depends('indent_id.indent_line_ids')
    def _compute_serial_no(self):
        for indent in self.mapped('indent_id'):
            lines = indent.indent_line_ids.sorted(key=lambda l: (
                1 if not isinstance(l.id, int) else 0,
                l.id or 0
            ))
            for idx, line in enumerate(lines, start=1):
                if line in self:
                    line.serial_no = idx
        # Fallback for lines not belonging to an indent
        for line in self:
            if not line.indent_id:
                line.serial_no = 0
    
    product_id = fields.Many2one(
        'product.product', 
        string='Product', 
        required=True,
        domain=[('type', 'in', ['product', 'consu'])]
    )
    
    product_name = fields.Char(
        string='Product Name', 
        help='Preserved product name from inventory',
        related='product_id.display_name',
        required=True
    )
    
    product_qty = fields.Float(
        string='Quantity', 
        digits='Product Unit of Measure', 
        default=1.0,
        required=True
    )
    
    uom_id = fields.Many2one(
        'uom.uom', 
        string='Unit of Measure',
        required=True
    )
    
    available_qty = fields.Float(
        string='Available Qty',
        digits='Product Unit of Measure',
        help='Current stock availability'
    )
    
    vendor_id = fields.Many2one(
        'res.partner',
        string='Preferred Vendor',
        compute='_compute_vendor_id',
        store=True
    )
    
    make = fields.Char(
        related='product_id.make',
        string='Make',
        readonly=True,
        store=True
    )
    description_short = fields.Char(
        related='product_id.description_short',
        string='Description',
        readonly=True,
        store=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('uom_id') and vals.get('product_id'):
                product = self.env['product.product'].browse(vals['product_id'])
                vals['uom_id'] = product.uom_id.id
        return super(MaterialIndentLine, self).create(vals_list)

    def write(self, vals):
        if 'product_id' in vals and not vals.get('uom_id'):
            product = self.env['product.product'].browse(vals['product_id'])
            vals['uom_id'] = product.uom_id.id
        return super(MaterialIndentLine, self).write(vals)

    @api.depends('product_id')
    def _compute_vendor_id(self):
        """Get preferred vendor from product"""
        for line in self:
            if line.product_id and line.product_id.seller_ids:
                line.vendor_id = line.product_id.seller_ids[0].partner_id
            else:
                line.vendor_id = False

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Auto-fill product details"""
        for rec in self:
            if rec.product_id:
                rec.uom_id = rec.product_id.uom_id.id
                rec.available_qty = rec.product_id.qty_available

    @api.constrains('product_qty')
    def _check_quantity(self):
        """Ensure positive quantity"""
        for line in self:
            if line.product_qty <= 0:
                raise ValidationError(_('Quantity must be greater than zero.'))