# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
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
    
    def _generate_custom_name(self, vals=None):
        """
        Generate custom purchase order reference in format:
        PA/ORDER/QTN-YY-YY/NNNN
        """
        # Get components
        prefix = "PA"
        middle = "ORDER"
        
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
        
        # Get sequential number from custom sequence
        seq_number = self.env['ir.sequence'].with_company(company).next_by_code('purchase.order.custom') or '0001'
        
        # Build full reference
        return f"{prefix}/{middle}/QTN-{fy}/{seq_number}"
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name', _("New")) == _("New") or vals.get('name') == 'New':
                # Generate custom name before creating record
                vals['name'] = self._generate_custom_name(vals)
        
        return super(PurchaseOrder, self).create(vals_list)
