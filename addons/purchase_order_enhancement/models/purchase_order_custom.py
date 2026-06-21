# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    custom_ref_code = fields.Char(
        string='Reference Code',
        default='00000',
        help='Custom reference code for PO (XXXXX part of PA/XXXXX/RFQ/QTN-YY-YY/NNNN)'
    )
    
    original_sequence = fields.Char(
        string='Original Sequence',
        help='Original sequence number for tracking',
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
    
    def _generate_custom_name(self, vals=None, use_original_seq=False):
        """
        Generate custom purchase order reference in format:
        PA/XXXXX/RFQ/QTN-YY-YY/NNNN
        """
        # Get components
        prefix = "PA"
        middle = "RFQ"
        
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
            # Use original sequence for revisions/updates
            seq_number = self.original_sequence
        else:
            # Generate new sequence
            seq_number = self.env['ir.sequence'].with_company(company).next_by_code('purchase.order.custom') or '0001'
        
        # Build full reference
        return f"{prefix}/{ref_code}/{middle}/QTN-{fy}/{seq_number}"
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name', _("New")) == _("New") or vals.get('name') == 'New':
                # Generate custom name before creating record
                vals['name'] = self._generate_custom_name(vals)
                
                # Extract sequence from generated name (last part)
                name_parts = vals['name'].split('/')
                if len(name_parts) >= 1:
                    seq_part = name_parts[-1]
                    vals['original_sequence'] = seq_part
        
        return super(PurchaseOrder, self).create(vals_list)
        
    def write(self, vals):
        # Update name if custom_ref_code is changed and order is in draft
        if 'custom_ref_code' in vals:
            for order in self:
                if order.state == 'draft':
                    # Prepare vals for generation
                    # We can't really pass vals easily to _generate_custom_name for self,
                    # but we can rely on the fact that we are writing to it.
                    # Actually, easier to let super write first, then update name.
                    pass 

        result = super(PurchaseOrder, self).write(vals)
        
        if 'custom_ref_code' in vals:
            for order in self:
                if order.state == 'draft':
                    new_name = order._generate_custom_name(use_original_seq=bool(order.original_sequence))
                    # Avoid recursion by using proper check or just directly writing if different
                    if new_name != order.name:
                        # We need to preserve the prefix state (PO vs RFQ)
                        # The generator defaults to RFQ.
                        # If current name has PO, we should respect that?
                        # But logic says ref code change is usually in draft where it is RFQ.
                        # Check current state just in case
                        if '/PO/' in order.name:
                            new_name = new_name.replace('/RFQ/', '/PO/')
                        
                        order.sudo().write({'name': new_name})
        return result

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            # If it goes straight to done (locked), it's a PO
            if order.state == 'done' and '/RFQ/' in order.name:
                order.name = order.name.replace('/RFQ/', '/PO/')
            # If it stays in purchase (confirmed) or to approve, it should remain RFQ
            # We check if it was somehow already PO (unlikely but safe)
            elif order.state in ['purchase', 'to approve'] and '/PO/' in order.name:
                order.name = order.name.replace('/PO/', '/RFQ/')
        return res
        
    def button_approve(self, force=False):
        res = super(PurchaseOrder, self).button_approve(force=force)
        for order in self:
            if order.state == 'done' and '/RFQ/' in order.name:
                order.name = order.name.replace('/RFQ/', '/PO/')
            elif order.state == 'purchase' and '/PO/' in order.name:
                order.name = order.name.replace('/PO/', '/RFQ/')
        return res

    def button_draft(self):
        res = super(PurchaseOrder, self).button_draft()
        for order in self:
            if '/PO/' in order.name:
                order.name = order.name.replace('/PO/', '/RFQ/')
        return res

    def button_done(self):
        res = super(PurchaseOrder, self).button_done()
        for order in self:
            if '/RFQ/' in order.name:
                order.name = order.name.replace('/RFQ/', '/PO/')
        return res

    def button_unlock(self):
        res = super(PurchaseOrder, self).button_unlock()
        for order in self:
            if '/PO/' in order.name:
                order.name = order.name.replace('/PO/', '/RFQ/')
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

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

