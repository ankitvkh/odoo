# File: models/gst_report.py

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import base64
from datetime import datetime


class GSTReport(models.Model):
    _name = 'gst.report'
    _description = 'GST Report'
    #_inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_from desc, id desc'

    name = fields.Char(
        string='Reference',
        required=True,
        readonly=True,
        default=lambda self: _('New'),
        copy=False,
        tracking=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        tracking=True
    )
    date_from = fields.Date(
        string='From Date',
        required=True,
        tracking=True
    )
    date_to = fields.Date(
        string='To Date',
        required=True,
        tracking=True
    )
    report_type = fields.Selection([
        ('gstr1', 'GSTR-1'),
        ('gstr3b', 'GSTR-3B')
    ], string='Report Type', required=True, tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('generated', 'Generated'),
        ('filed', 'Filed')
    ], string='Status', default='draft', tracking=True)

    total_taxable_value = fields.Monetary(
        string='Total Taxable Value',
        compute='_compute_totals',
        store=True,
        currency_field='company_currency_id'
    )
    total_igst = fields.Monetary(
        string='Total IGST',
        compute='_compute_totals',
        store=True,
        currency_field='company_currency_id'
    )
    total_cgst = fields.Monetary(
        string='Total CGST',
        compute='_compute_totals',
        store=True,
        currency_field='company_currency_id'
    )
    total_sgst = fields.Monetary(
        string='Total SGST',
        compute='_compute_totals',
        store=True,
        currency_field='company_currency_id'
    )

    company_currency_id = fields.Many2one(
        related='company_id.currency_id',
        string='Company Currency',
        readonly=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('gst.report') or _('New')
        return super().create(vals_list)

    def action_generate_report(self):
        self.ensure_one()
        try:
            if self.report_type == 'gstr1':
                data = self._generate_gstr1_data()
            else:
                data = self._generate_gstr3b_data()

            # Update report data and state
            self.write({
                'state': 'generated',
                # Update summary fields
                'total_taxable_value': data['total_taxable_value'],
                'total_igst': data['total_igst'],
                'total_cgst': data['total_cgst'],
                'total_sgst': data['total_sgst'],
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Report generated successfully'),
                    'sticky': False,
                    'type': 'success',
                }
            }
        except Exception as e:
            raise UserError(_('Error generating report: %s') % str(e))

    def action_mark_as_filed(self):
        """Mark the report as filed"""
        self.ensure_one()
        if self.state != 'generated':
            raise UserError(_('Only generated reports can be marked as filed.'))

        self.write({'state': 'filed'})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Report marked as filed'),
                'sticky': False,
                'type': 'success',
            }
        }

    @api.depends('report_type', 'date_from', 'date_to')
    def _compute_totals(self):
        """Compute report totals"""
        for report in self:
            # Get relevant invoices
            domain = [
                ('company_id', '=', report.company_id.id),
                ('date', '>=', report.date_from),
                ('date', '<=', report.date_to),
                ('state', '=', 'posted'),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
            ]
            invoices = self.env['account.move'].search(domain)

            # Initialize totals
            taxable_value = 0.0
            total_igst = 0.0
            total_cgst = 0.0
            total_sgst = 0.0

            # Calculate totals from invoices
            for invoice in invoices:
                taxable_value += invoice.amount_untaxed

                for tax_line in invoice.line_ids.filtered(lambda l: l.tax_line_id):
                    tax_group = tax_line.tax_line_id.tax_group_id.name
                    tax_amount = tax_line.balance

                    if tax_group == 'IGST':
                        total_igst += abs(tax_amount)
                    elif tax_group == 'CGST':
                        total_cgst += abs(tax_amount)
                    elif tax_group == 'SGST':
                        total_sgst += abs(tax_amount)

            # Update report values
            report.total_taxable_value = taxable_value
            report.total_igst = total_igst
            report.total_cgst = total_cgst
            report.total_sgst = total_sgst

    def _generate_gstr1_data(self):
        # Get relevant invoices
        domain = [
            ('company_id', '=', self.company_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('state', '=', 'posted'),
        ]
        invoices = self.env['account.move'].search(domain)

        total_taxable = 0.0
        total_igst = 0.0
        total_cgst = 0.0
        total_sgst = 0.0

        for invoice in invoices:
            total_taxable += invoice.amount_untaxed
            for tax_line in invoice.line_ids.filtered(lambda l: l.tax_line_id):
                tax_group = tax_line.tax_line_id.tax_group_id.name
                tax_amount = abs(tax_line.balance)
                if tax_group == 'IGST':
                    total_igst += tax_amount
                elif tax_group == 'CGST':
                    total_cgst += tax_amount
                elif tax_group == 'SGST':
                    total_sgst += tax_amount

        return {
            'total_taxable_value': total_taxable,
            'total_igst': total_igst,
            'total_cgst': total_cgst,
            'total_sgst': total_sgst,
        }

    def _generate_gstr3b_data(self):
        # Similar to GSTR1 but with GSTR3B specific calculations
        domain = [
            ('company_id', '=', self.company_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('state', '=', 'posted'),
        ]
        invoices = self.env['account.move'].search(domain)

        total_taxable = 0.0
        total_igst = 0.0
        total_cgst = 0.0
        total_sgst = 0.0

        for invoice in invoices:
            if invoice.move_type in ['out_invoice', 'out_refund']:
                sign = -1 if invoice.move_type == 'out_refund' else 1
                total_taxable += sign * invoice.amount_untaxed
                for tax_line in invoice.line_ids.filtered(lambda l: l.tax_line_id):
                    tax_group = tax_line.tax_line_id.tax_group_id.name
                    tax_amount = abs(tax_line.balance) * sign
                    if tax_group == 'IGST':
                        total_igst += tax_amount
                    elif tax_group == 'CGST':
                        total_cgst += tax_amount
                    elif tax_group == 'SGST':
                        total_sgst += tax_amount

        return {
            'total_taxable_value': total_taxable,
            'total_igst': total_igst,
            'total_cgst': total_cgst,
            'total_sgst': total_sgst,
        }