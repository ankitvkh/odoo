from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_in_gst_treatment = fields.Selection([
        ('regular', 'Registered Business - Regular'),
        ('composition', 'Registered Business - Composition'),
        ('unregistered', 'Unregistered Business'),
        ('consumer', 'Consumer'),
        ('overseas', 'Overseas'),
        ('special_economic_zone', 'Special Economic Zone'),
        ('deemed_export', 'Deemed Export'),
        ('uin_holders', 'UIN Holders'),
    ], string='GST Treatment', default='regular')

    l10n_in_gst_eligible = fields.Boolean(
        string='GST Eligible',
        compute='_compute_l10n_in_gst_eligible',
        store=True
    )

    l10n_in_hsn_code = fields.Char(
        string='HSN Code',
        compute='_compute_l10n_in_hsn_code',
        store=True
    )

    l10n_in_export_type = fields.Selection([
        ('with_payment', 'With Payment of Tax'),
        ('without_payment', 'Without Payment of Tax'),
    ], string='Export Type')

    @api.depends('move_type', 'partner_id', 'company_id')
    def _compute_l10n_in_gst_eligible(self):
        for move in self:
            move.l10n_in_gst_eligible = (
                    move.move_type in ('out_invoice', 'out_refund') and
                    move.company_id.country_id.code == 'IN' and
                    not move.company_id.l10n_in_gst_composition
            )

    @api.depends('invoice_line_ids.product_id')
    def _compute_l10n_in_hsn_code(self):
        for move in self:
            hsn_codes = move.invoice_line_ids.mapped('product_id.l10n_in_hsn_code')
            move.l10n_in_hsn_code = ', '.join(filter(None, hsn_codes))

    @api.constrains('l10n_in_gst_treatment', 'partner_id')
    def _check_gst_treatment(self):
        for move in self:
            if move.l10n_in_gst_treatment == 'regular' and not move.partner_id.vat:
                raise ValidationError(_(
                    'GST Treatment is set to "Regular" but partner %s does not have a GSTIN.',
                    move.partner_id.name
                ))

    def _prepare_gstr1_values(self):
        """Prepare values for GSTR-1 reporting"""
        self.ensure_one()
        return {
            'invoice_no': self.name,
            'invoice_date': self.date.strftime('%d-%m-%Y'),
            'invoice_value': self.amount_total,
            'place_of_supply': self.partner_id.state_id.l10n_in_tin,
            'reverse_charge': 'N',
            'invoice_type': self._get_gstr1_invoice_type(),
            'export_type': self.l10n_in_export_type if self.l10n_in_gst_treatment == 'overseas' else '',
            'rate': self._get_gst_tax_rate(),
            'taxable_value': self.amount_untaxed,
            'tax_amount': self.amount_tax,
            'hsn_summary': self._get_hsn_summary(),
        }

    def _get_gstr1_invoice_type(self):
        """Get invoice type for GSTR-1"""
        self.ensure_one()
        if self.move_type == 'out_refund':
            return 'CR'
        if self.l10n_in_gst_treatment == 'overseas':
            return 'EXP'
        if self.l10n_in_gst_treatment == 'special_economic_zone':
            return 'SEZ'
        return 'R'

    def _get_gst_tax_rate(self):
        """Calculate GST rate for the invoice"""
        self.ensure_one()
        # Get the first line's tax rate as representative
        for line in self.invoice_line_ids:
            if line.tax_ids:
                return sum(line.tax_ids.mapped('amount'))
        return 0.0

    def _get_hsn_summary(self):
        """Get HSN-wise summary for the invoice"""
        self.ensure_one()
        hsn_dict = {}

        for line in self.invoice_line_ids.filtered(lambda l: not l.display_type):
            hsn = line.product_id.l10n_in_hsn_code or 'NO-HSN'

            if hsn not in hsn_dict:
                hsn_dict[hsn] = {
                    'hsn_code': hsn,
                    'quantity': 0,
                    'taxable_value': 0,
                    'igst': 0,
                    'cgst': 0,
                    'sgst': 0,
                    'cess': 0,
                }

            hsn_data = hsn_dict[hsn]
            hsn_data['quantity'] += line.quantity
            hsn_data['taxable_value'] += line.price_subtotal

            # Calculate tax amounts
            for tax in line.tax_ids:
                tax_amount = line.price_subtotal * (tax.amount / 100)
                if tax.tax_group_id.name == 'IGST':
                    hsn_data['igst'] += tax_amount
                elif tax.tax_group_id.name == 'CGST':
                    hsn_data['cgst'] += tax_amount
                elif tax.tax_group_id.name == 'SGST':
                    hsn_data['sgst'] += tax_amount
                elif tax.tax_group_id.name == 'Cess':
                    hsn_data['cess'] += tax_amount

        return list(hsn_dict.values())