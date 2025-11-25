# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    def _get_invoice_reference_indian(self):
        """Override to return 'Tax Invoice' instead of default"""
        self.ensure_one()
        if self.move_type == 'out_invoice':
            if self.state == 'draft':
                return _('Draft Tax Invoice')
            else:
                return _('Tax Invoice')
        elif self.move_type == 'out_refund':
            return _('Credit Note')
        elif self.move_type == 'in_invoice':
            return _('Vendor Bill')
        elif self.move_type == 'in_refund':
            return _('Vendor Credit Note')
        return super()._get_invoice_reference_indian()
    
    @api.model
    def _get_default_currency(self):
        """Set default currency to INR"""
        inr_currency = self.env['res.currency'].search([('name', '=', 'INR')], limit=1)
        if inr_currency:
            return inr_currency.id
        return super()._get_default_currency()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    # Override display names for tax-related fields
    def _get_tax_display_name(self):
        """Return GST instead of Tax"""
        return _('GST')
