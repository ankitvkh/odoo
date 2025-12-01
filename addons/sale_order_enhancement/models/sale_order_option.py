# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'
    
    tax_id = fields.Many2many(
        'account.tax',
        string='Taxes',
        domain="[('type_tax_use', '=', 'sale'), ('company_id', '=', company_id)]",
        help='Taxes applied to this optional product'
    )
    
    price_tax = fields.Float(
        string='Tax Amount',
        compute='_compute_amount',
        store=True
    )
    
    price_total = fields.Float(
        string='Total',
        compute='_compute_amount',
        store=True
    )
    
    price_subtotal = fields.Float(
        string='Subtotal',
        compute='_compute_amount',
        store=True
    )
    
    display_type = fields.Selection([
        ('line_section', 'Section'),
        ('line_note', 'Note'),
    ], string='Display Type', default=False)
    
    company_id = fields.Many2one(
        'res.company',
        related='order_id.company_id',
        store=True,
        readonly=True
    )
    
    @api.depends('quantity', 'price_unit', 'discount', 'tax_id')
    def _compute_amount(self):
        """Compute the amounts of the optional product line."""
        for option in self:
            if option.display_type:
                option.price_subtotal = 0.0
                option.price_tax = 0.0
                option.price_total = 0.0
                continue
                
            price = option.price_unit * (1 - (option.discount or 0.0) / 100.0)
            option.price_subtotal = price * option.quantity
            
            if option.tax_id:
                taxes = option.tax_id.compute_all(
                    price,
                    option.order_id.currency_id,
                    option.quantity,
                    product=option.product_id,
                    partner=option.order_id.partner_id
                )
                option.price_tax = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                option.price_total = taxes['total_included']
            else:
                option.price_tax = 0.0
                option.price_total = option.price_subtotal
