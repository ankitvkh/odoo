# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    custom_ref_code = fields.Char(
        string='Reference Code',
        default='00000',
        help='Custom reference code for quotation (XXXXX part of RASP/XXXXX/QTN-YY-YY/NNNN)'
    )
    
    offer_type = fields.Selection([
        ('actual', 'Actual Offer'),
        ('technical', 'Technical Offer'),
        ('budgetary', 'Budgetary Offer'),
    ], string='Offer Type', default='actual', required=False,
       help='Select offer type: Actual Offer/Budgetary Offer shows real prices, Technical Offer shows "Quoted Price"')
    
    portal_ref_no = fields.Char(
        string='Portal Ref. No.',
        help='Reference number from the portal, only for Technical Offers'
    )
    
    # Computed fields for conditional price display
    amount_untaxed_display = fields.Char(
        string='Basic Amount',
        compute='_compute_amount_display',
        help='Displays actual amount or "Quoted Price" based on offer type'
    )
    
    amount_tax_display = fields.Char(
        string='Taxes',
        compute='_compute_amount_display',
        help='Displays actual tax or "Quoted Price" based on offer type'
    )
    
    amount_total_display = fields.Char(
        string='Total',
        compute='_compute_amount_display',
        help='Displays actual total or "Quoted Price" based on offer type'
    )
    
    revision_count = fields.Integer(
        string='Revision Count',
        default=0,
        help='Number of times this quotation has been revised after being sent (0 = original)'
    )
    
    original_sequence = fields.Char(
        string='Original Sequence',
        help='Original sequence number for tracking revisions',
        copy=False
    )
    
    is_revised = fields.Boolean(
        string='Is Revised',
        help='Internal flag to track if the quotation has been modified since last send',
        default=False,
        copy=False
    )
    
    def _get_financial_year(self, date):
        """
        Calculate financial year based on date.
        Assumes FY starts in April (common in many countries).
        Returns format like '25-26' for FY 2025-2026.
        """
        if not date:
            date = fields.Date.today()
        
        year = date.year
        month = date.month
        
        # If month is April or later, FY is current year to next year
        # If month is before April, FY is previous year to current year
        if month >= 4:
            fy_start = year
            fy_end = year + 1
        else:
            fy_start = year - 1
            fy_end = year
        
        # Format as YY-YY (e.g., 25-26)
        return f"{str(fy_start)[-2:]}-{str(fy_end)[-2:]}"
    
    @api.depends('offer_type', 'amount_untaxed', 'amount_tax', 'amount_total')
    def _compute_amount_display(self):
        """
        Compute display values for amounts based on offer type.
        Technical offers show "Quoted Price", Actual offers show real amounts.
        """
        for order in self:
            if order.offer_type == 'technical':
                order.amount_untaxed_display = 'Quoted'
                order.amount_tax_display = 'Quoted'
                order.amount_total_display = 'Quoted'
            else:
                # Format amounts with currency (for actual and budgetary)
                currency = order.currency_id or order.company_id.currency_id
                order.amount_untaxed_display = f"{currency.symbol} {order.amount_untaxed:,.2f}"
                order.amount_tax_display = f"{currency.symbol} {order.amount_tax:,.2f}"
                order.amount_total_display = f"{currency.symbol} {order.amount_total:,.2f}"
    
    def _generate_custom_name(self, vals=None, use_original_seq=False, explicit_revision=None):
        """
        Generate custom quotation reference in format:
        RASP/XXXXX/QTN-YY-YY/NNNN or RASP/XXXXX/QTN-YY-YY/NNNNA (for revisions)
        """
        # Get components
        prefix = "RASP"
        
        # Determine ref_code
        ref_code = "00000"
        if vals and 'custom_ref_code' in vals:
            ref_code = vals['custom_ref_code'] or "00000"
        elif self:
            ref_code = self.custom_ref_code or "00000"
            
        # Determine date for FY
        date_order = fields.Date.today()
        if vals and 'date_order' in vals:
            date_order = fields.Datetime.to_datetime(vals['date_order'])
        elif self:
            date_order = self.date_order or fields.Date.today()
            
        fy = self._get_financial_year(date_order)
        
        # Determine company
        company = self.env.company
        if vals and 'company_id' in vals:
            company = self.env['res.company'].browse(vals['company_id'])
        elif self:
            company = self.company_id or self.env.company
        
        # Get sequential number
        if use_original_seq and self and self.original_sequence:
            # Use original sequence for revisions
            seq_number = self.original_sequence
        else:
            # Generate new sequence with fallback
            try:
                seq_number = self.env['ir.sequence'].with_company(company).next_by_code('sale.order.custom')
                if not seq_number:
                    # Fallback to default Odoo sequence if custom one is missing
                    seq_number = self.env['ir.sequence'].with_company(company).next_by_code('sale.order') or '0001'
            except Exception:
                seq_number = '0001'
        
        # Build base reference
        base_name = f"{prefix}/{ref_code}/QTN-{fy}/{seq_number}"
        
        # Add revision suffix if this is a revision (A, B, C, etc.)
        revision = 0
        if explicit_revision is not None:
            # Use explicitly provided revision count
            revision = explicit_revision
        elif vals and 'revision_count' in vals:
            revision = vals['revision_count']
        elif self:
            revision = self.revision_count or 0
        
        if revision > 0:
            # Convert to alphabetical: 1=A, 2=B, 3=C, etc.
            suffix = chr(64 + revision)  # 65 is 'A'
            return f"{base_name}{suffix}"
        
        return base_name
    
    @api.model_create_multi
    def create(self, vals_list):
        is_test = self.env.registry.in_test_mode() or tools.config.get('test_enable') or tools.config.get('test_file')
        for vals in vals_list:
            # Only generate custom name if it's a new record and not being loaded from demo/fixed data
            if not vals.get('name') or vals.get('name', _("New")) == _("New") or vals.get('name') == 'New':
                # Skip custom name generation if we are in demo mode or if specifically requested via context
                if not self.env.context.get('skip_custom_name_generation') and not is_test:
                    vals['name'] = self._generate_custom_name(vals)
                
                # Store original sequence if this is not a revision
                if vals.get('revision_count', 0) == 0 and vals.get('name') and '/' in vals['name']:
                    # Extract sequence from generated name
                    name_parts = vals['name'].split('/')
                    if len(name_parts) >= 4:
                        seq_part = name_parts[-1]
                        if seq_part and seq_part[-1].isalpha():
                            seq_part = seq_part[:-1]
                        vals['original_sequence'] = seq_part
        
        return super(SaleOrder, self).create(vals_list)
    
    def write(self, vals):
        # Recursion guard using context
        if self.env.context.get('skip_revision_tracking'):
            return super(SaleOrder, self).write(vals)

        # Track which orders need revision flag incremented
        orders_to_revise = self.env['sale.order']
        
        # Exclude certain fields that shouldn't trigger revision
        excluded_fields = {'message_follower_ids', 'message_ids', 'activity_ids', 
                         'access_token', 'state', 'revision_count', 'name', 'is_revised'}
        
        # Check if any meaningful field is being changed
        meaningful_change = any(key not in excluded_fields for key in vals.keys())
        
        if meaningful_change:
            for order in self:
                # Increment revision if order was previously sent and not being cancelled
                if order.state == 'sent' and vals.get('state') != 'cancel':
                    orders_to_revise |= order
        
        result = super(SaleOrder, self).write(vals)
        
        # Flag as revised
        if orders_to_revise:
            orders_to_revise.sudo().with_context(skip_revision_tracking=True).write({
                'is_revised': True
            })
        
        # Handle Custom Name regeneration for Draft orders
        if 'custom_ref_code' in vals:
            is_test = self.env.registry.in_test_mode() or tools.config.get('test_enable') or tools.config.get('test_file')
            for order in self:
                if order.state == 'draft' and not is_test:
                    new_name = order._generate_custom_name(use_original_seq=bool(order.original_sequence))
                    order.sudo().with_context(skip_revision_tracking=True).write({
                        'name': new_name
                    })
        
        return result

    def action_quotation_send(self):
        """
        Overridden to increment revision count if the order has been revised
        """
        res = super(SaleOrder, self).action_quotation_send()
        for order in self:
            if order.is_revised and order.state == 'sent':
                new_revision = (order.revision_count or 0) + 1
                # Generate new name with the incremented revision count
                new_name = order._generate_custom_name(use_original_seq=True, explicit_revision=new_revision)
                # Apply the revision increment and name update using context guard
                order.sudo().with_context(skip_revision_tracking=True).write({
                    'revision_count': new_revision,
                    'is_revised': False,
                    'name': new_name
                })
        return res




class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    make = fields.Char(related='product_id.make', string='Make', readonly=True)
    description_short = fields.Char(related='product_id.description_short', string='Short Description', readonly=True)
    
    alias = fields.Char(
        string='Alias',
        compute='_compute_alias',
        inverse='_inverse_alias',
        store=False,
    )

    @api.depends('order_id', 'product_id')
    def _compute_alias(self):
        order_ids = self.mapped('order_id').ids
        product_ids = self.mapped('product_id').ids
        aliases = self.env['sale.product.alias'].search([
            ('order_id', 'in', order_ids),
            ('product_id', 'in', product_ids)
        ])
        alias_map = {(a.order_id.id, a.product_id.id): a.alias for a in aliases}
        for line in self:
            line.alias = alias_map.get((line.order_id.id, line.product_id.id), '')

    def _inverse_alias(self):
        for line in self:
            if not line.order_id or not line.product_id:
                continue
            order_id = line.order_id.id
            if not order_id or isinstance(order_id, models.NewId):
                continue
            self.env['sale.product.alias']._set_alias(order_id, line.product_id.id, line.alias or '')

    
    offer_type = fields.Selection(
        selection=[
            ('actual', 'Actual Offer'),
            ('technical', 'Technical Offer'),
            ('budgetary', 'Budgetary Offer'),
        ],
        string='Offer Type',
        compute='_compute_offer_type',
        store=False,
        readonly=True
    )
    
    serial_no = fields.Integer(
        string='Sr. No.',
        compute='_compute_serial_no',
        store=False
    )
    
    @api.depends('order_id.order_line')
    def _compute_serial_no(self):
        """
        Optimized serial number computation to avoid O(N^2) complexity.
        Computes serial numbers for all lines in the order in one pass.
        """
        # Group by order to compute everything at once
        orders = self.mapped('order_id')
        for order in orders:
            # Sort lines once per order, pushing new/draft lines (NewId) to the end
            lines = order.order_line.sorted(key=lambda l: (1 if not isinstance(l.id, int) else 0, l.sequence or 0))
            for idx, line in enumerate(lines, start=1):
                # Only update lines that are in the current batch (self)
                if line in self:
                    line.serial_no = idx
        
        # Handle lines without an order_id
        for line in self:
            if not line.order_id:
                line.serial_no = 0

    
    @api.depends('order_id.offer_type')
    def _compute_offer_type(self):
        for line in self:
            # Use order_id.offer_type if available, otherwise check context (for new lines)
            line.offer_type = line.order_id.offer_type or self.env.context.get('default_offer_type') or 'actual'

    # Computed fields for conditional price display
    price_unit_display = fields.Char(
        string='Unit Price Display',
        compute='_compute_amount_display',
        help='Displays actual price or "Quoted Price" based on offer type'
    )
    
    price_subtotal_display = fields.Char(
        string='Subtotal Display',
        compute='_compute_amount_display',
        help='Displays actual subtotal or "Quoted Price" based on offer type'
    )
    
    price_tax_display = fields.Char(
        string='Tax Display',
        compute='_compute_amount_display',
        help='Displays actual tax or "Quoted Price" based on offer type'
    )
    
    price_total_display = fields.Char(
        string='Total Display',
        compute='_compute_amount_display',
        help='Displays actual total or "Quoted Price" based on offer type'
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        lines = super(SaleOrderLine, self).create(vals_list)
        for line, vals in zip(lines, vals_list):
            if 'alias' in vals and vals['alias'] and line.order_id and line.product_id:
                self.env['sale.product.alias']._set_alias(line.order_id.id, line.product_id.id, vals['alias'])
        return lines

    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)
        if 'alias' in vals:
            for line in self:
                if line.order_id and line.product_id:
                    self.env['sale.product.alias']._set_alias(line.order_id.id, line.product_id.id, vals['alias'] or '')
        return res


    @api.depends('offer_type', 'price_unit', 'price_subtotal', 'price_tax', 'price_total')
    def _compute_amount_display(self):
        """
        Compute display values for amounts based on offer type.
        Technical offers show "Quoted Price", Actual offers show real amounts.
        """
        for line in self:
            if line.offer_type == 'technical':
                line.price_unit_display = 'Quoted'
                line.price_subtotal_display = 'Quoted'
                line.price_tax_display = 'Quoted'
                line.price_total_display = 'Quoted'
            else:
                # Format amounts with currency (for actual and budgetary)
                currency = line.currency_id or line.company_id.currency_id
                line.price_unit_display = f"{currency.symbol} {line.price_unit:,.2f}"
                line.price_subtotal_display = f"{currency.symbol} {line.price_subtotal:,.2f}"
                line.price_tax_display = f"{currency.symbol} {line.price_tax:,.2f}"
                line.price_total_display = f"{currency.symbol} {line.price_total:,.2f}"


class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'
    
    make = fields.Char(related='product_id.make', string='Make', readonly=True)
    description_short = fields.Char(related='product_id.description_short', string='Short Description', readonly=True)
    
    offer_type = fields.Selection(
        selection=[
            ('actual', 'Actual Offer'),
            ('technical', 'Technical Offer'),
            ('budgetary', 'Budgetary Offer'),
        ],
        string='Offer Type',
        compute='_compute_offer_type',
        store=True,
        readonly=True
    )
    
    serial_no = fields.Integer(
        string='Sr. No.',
        compute='_compute_serial_no',
        store=False
    )
    
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)
    currency_id = fields.Many2one(related='order_id.currency_id', depends=['order_id.currency_id'], store=True, string='Currency')

    @api.depends('order_id', 'order_id.sale_order_option_ids')
    def _compute_serial_no(self):
        for line in self:
            if line.order_id:
                # Get all option lines in the order, sorted by sequence
                lines = line.order_id.sale_order_option_ids.sorted('sequence')
                # Calculate serial number based on position in the list
                serial = 1
                for idx, option_line in enumerate(lines, start=1):
                    if option_line == line:
                        serial = idx
                        break
                line.serial_no = serial
            else:
                line.serial_no = 0

    @api.depends('quantity', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO option line.
        """
        for line in self:
            tax_results = line.tax_id.compute_all(
                line.price_unit,
                line.order_id.currency_id,
                line.quantity,
                line.product_id,
                line.order_id.partner_id
            )
            amount_untaxed = tax_results['total_excluded']
            amount_tax = tax_results['total_included'] - amount_untaxed

            line.update({
                'price_subtotal': amount_untaxed,
                'price_tax': amount_tax,
                'price_total': tax_results['total_included'],
            })

    def _convert_to_tax_base_line_dict(self):
        """ Convert the current record to a dictionary in order to use the generic taxes computation method
        defined on account.tax.

        :return: A python dictionary.
        """
        self.ensure_one()
        return self.env['account.tax']._convert_to_tax_base_line_dict(
            self,
            partner=self.order_id.partner_id,
            currency=self.order_id.currency_id,
            product=self.product_id,
            taxes=self.tax_id,
            price_unit=self.price_unit,
            quantity=self.quantity,
            discount=self.discount,
            price_subtotal=self.price_subtotal,
        )

    
    @api.depends('order_id.offer_type')
    def _compute_offer_type(self):
        for line in self:
            # Use order_id.offer_type if available, otherwise check context (for new lines)
            line.offer_type = line.order_id.offer_type or self.env.context.get('default_offer_type') or 'actual'
    
    # Computed fields for conditional price display
    price_unit_display = fields.Char(
        string='Unit Price Display',
        compute='_compute_amount_display',
        help='Displays actual price or "Quoted Price" based on offer type'
    )
    
    price_subtotal_display = fields.Char(
        string='Subtotal Display',
        compute='_compute_amount_display',
        help='Displays actual subtotal or "Quoted Price" based on offer type'
    )
    
    price_tax_display = fields.Char(
        string='Tax Display',
        compute='_compute_amount_display',
        help='Displays actual tax or "Quoted Price" based on offer type'
    )
    
    price_total_display = fields.Char(
        string='Total Display',
        compute='_compute_amount_display',
        help='Displays actual total or "Quoted Price" based on offer type'
    )
    
    @api.depends('offer_type', 'price_unit', 'price_subtotal', 'price_tax', 'price_total')
    def _compute_amount_display(self):
        """
        Compute display values for amounts based on offer type.
        Technical offers show "Quoted Price", Actual offers show real amounts.
        """
        for line in self:
            if line.offer_type == 'technical':
                line.price_unit_display = 'Quoted'
                line.price_subtotal_display = 'Quoted'
                line.price_tax_display = 'Quoted'
                line.price_total_display = 'Quoted'
            else:
                # Format amounts with currency (for actual and budgetary)
                # sale.order.option doesn't have currency_id, use order_id's currency
                currency = line.currency_id or line.company_id.currency_id
                line.price_unit_display = f"{currency.symbol} {line.price_unit:,.2f}"
                
                # Use the new computed fields
                subtotal = line.price_subtotal
                tax = line.price_tax
                total = line.price_total
                
                line.price_subtotal_display = f"{currency.symbol} {subtotal:,.2f}"
                line.price_tax_display = f"{currency.symbol} {tax:,.2f}"
                line.price_total_display = f"{currency.symbol} {total:,.2f}"


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.model_create_multi
    def create(self, vals_list):
        taxes = super(AccountTax, self).create(vals_list)
        for tax in taxes:
            tax._ensure_unique_tax_group()
        return taxes

    def write(self, vals):
        res = super(AccountTax, self).write(vals)
        if 'name' in vals or 'tax_group_id' in vals:
            for tax in self:
                tax._ensure_unique_tax_group()
        return res

    def _ensure_unique_tax_group(self):
        """
        Ensure that the tax has a unique tax group matching its name,
        so that it renders as an independent line in the subtotal footer
        with its exact tax configuration name.
        """
        self.ensure_one()
        group_name = self.name
        company_id = self.company_id.id or self.env.company.id
        tax_group = self.env['account.tax.group'].sudo().search([
            ('name', '=', group_name),
            ('company_id', '=', company_id)
        ], limit=1)
        if not tax_group:
            tax_group = self.env['account.tax.group'].sudo().create({
                'name': group_name,
                'company_id': company_id
            })
        
        if self.tax_group_id != tax_group:
            self.sudo().with_context(skip_revision_tracking=True).write({
                'tax_group_id': tax_group.id
            })
        elif tax_group.name != self.name:
            tax_group.sudo().write({'name': self.name})


class SaleProductAlias(models.Model):
    _name = 'sale.product.alias'
    _description = 'Sale Product Alias'

    order_id = fields.Many2one('sale.order', string='Sales Order', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True, ondelete='cascade')
    alias = fields.Char(string='Alias')

    _sql_constraints = [
        ('order_product_uniq', 'unique(order_id, product_id)', 'The alias must be unique per Sales Order and Product.')
    ]

    @api.model
    def _set_alias(self, order_id, product_id, alias_val):
        alias_record = self.search([
            ('order_id', '=', order_id),
            ('product_id', '=', product_id)
        ], limit=1)
        if alias_record:
            if alias_val:
                alias_record.write({'alias': alias_val})
            else:
                alias_record.unlink()
        elif alias_val:
            self.create({
                'order_id': order_id,
                'product_id': product_id,
                'alias': alias_val,
            })

