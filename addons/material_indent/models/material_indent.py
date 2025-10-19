from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MaterialIndent(models.Model):
    _name = 'material.indent'
    _description = 'Material Indent'
    _order = 'id desc'

    name = fields.Char(string='Indent Reference', required=True, copy=False, readonly=True, default='New')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', readonly=True)

    bom_id = fields.Many2one('mrp.bom', string='BOM', required=True)
    project_id = fields.Many2one('project.project', string='Project')
    indent_line_ids = fields.One2many('material.indent.line', 'indent_id', string='Lines', copy=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq = self.env.ref('material_indent.sequence_material_indent')
            vals['name'] = seq.next_by_id() if seq else 'INDENT/NEW'
        return super().create(vals)

    def action_load_from_bom(self):
        self.ensure_one()
        bom = self.bom_id
        # set project for project flow
        if bom.bom_flow_type == 'project' and bom.project_id:
            self.project_id = bom.project_id.id
        # map bom lines to indent lines
        lines = []
        for line in bom.bom_line_ids:
            product = line.product_id
            # For spare flow, enforce exact name match between BOM and product
            if bom.bom_flow_type == 'spare':
                if bom.product_tmpl_id and bom.product_tmpl_id.name != product.name:
                    raise ValidationError(_('Spare parts flow requires BOM name to match product name: %s vs %s') % (bom.product_tmpl_id.name, product.name))
            lines.append((0, 0, {
                'product_id': product.id,
                'product_name': product.name,
                'product_qty': line.product_qty,
                'uom_id': line.product_uom_id.id,
            }))
        self.indent_line_ids = [(5, 0, 0)] + lines
        return True

    def action_submit(self):
        for rec in self:
            if not rec.indent_line_ids:
                raise ValidationError(_('Cannot submit an empty indent.'))
            rec.state = 'submitted'

    def action_approve(self):
        for rec in self:
            rec.state = 'approved'
            rec._create_purchase_orders()

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def _create_purchase_orders(self):
        PurchaseOrder = self.env['purchase.order']
        partner_map = {}
        for line in self.indent_line_ids:
            sellers = line.product_id.seller_ids
            partner = sellers and sellers[0].name or self.env['res.partner']
            partner_map.setdefault(partner.id, []).append(line)

        for partner_id, lines in partner_map.items():
            po = PurchaseOrder.create({
                'partner_id': partner_id,
                'company_id': self.company_id.id,
                'origin': self.name,
            })
            pol = []
            for l in lines:
                pol.append((0, 0, {
                    'product_id': l.product_id.id,
                    'name': l.product_name,
                    'product_qty': l.product_qty,
                    'product_uom': l.uom_id.id,
                    'price_unit': l.product_id.standard_price,
                }))
            po.order_line = pol


class MaterialIndentLine(models.Model):
    _name = 'material.indent.line'
    _description = 'Material Indent Line'

    indent_id = fields.Many2one('material.indent', string='Indent', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_name = fields.Char('Product Name', help='Preserved product name from inventory')
    product_qty = fields.Float('Quantity', digits='Product Unit of Measure', default=1.0)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            rec.product_name = rec.product_id.name
            if not rec.uom_id:
                rec.uom_id = rec.product_id.uom_id.id
