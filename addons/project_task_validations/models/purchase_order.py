# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    preferred_vendors_only = fields.Boolean(
        string='Preferred Vendors Only',
        help='Show only preferred vendors for selected products',
        default=True
    )

    def _validate_preferred_vendor(self):
        """Validate if the selected vendor is preferred for all products"""
        if self.preferred_vendors_only and self.order_line:
            for line in self.order_line:
                if line.product_id:
                    preferred_vendors = line.product_id.product_tmpl_id.preferred_vendor_ids
                    if preferred_vendors and self.partner_id not in preferred_vendors:
                        raise ValidationError(_(
                            'Vendor %s is not in the preferred vendors list for product: %s\n'
                            'Please select one of the preferred vendors for this product.',
                            self.partner_id.name,
                            line.product_id.name
                        ))

    @api.onchange('partner_id')
    def _check_preferred_vendor(self):
        try:
            self._validate_preferred_vendor()
        except ValidationError as e:
            # Reset partner_id if validation fails
            self.partner_id = False
            return {
                'warning': {
                    'title': _('Error!'),
                    'message': str(e)
                }
            }

    @api.constrains('partner_id', 'order_line', 'preferred_vendors_only')
    def _check_preferred_vendor_constraint(self):
        for order in self:
            order._validate_preferred_vendor()

    def button_confirm(self):
        """Inherit confirm button to add validation"""
        self._validate_preferred_vendor()
        return super().button_confirm()

    def action_rfq_send(self):
        """Inherit send RFQ action to add validation"""
        self._validate_preferred_vendor()
        return super().action_rfq_send()

    def print_quotation(self):
        """Inherit print action to add validation"""
        self._validate_preferred_vendor()
        return super().print_quotation()

    def write(self, vals):
        """Inherit write to validate on save"""
        res = super().write(vals)
        if not self.env.context.get('skip_preferred_vendor_check'):
            self._validate_preferred_vendor()
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id')
    def _onchange_product_selection(self):
        if self.product_id and self.order_id:
            _logger.info(f'Product changed to: {self.product_id.name}')
            preferred_vendors = self.product_id.product_tmpl_id.preferred_vendor_ids

            if preferred_vendors:
                preferred_vendor = preferred_vendors[0]
                _logger.info(f'Found preferred vendor: {preferred_vendor.name}')

                # Update the parent order's vendor if not set
                if not self.order_id.partner_id:
                    self.order_id.partner_id = preferred_vendor
                    _logger.info(f'Updated PO vendor to: {preferred_vendor.name}')