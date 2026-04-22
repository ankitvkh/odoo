# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    make = fields.Char(
        string='Make',
        help='Manufacturer or Brand of the product'
    )
    description_short = fields.Char(
        string='Short Description',
        help='A brief description for identification in lists'
    )

    @api.depends('name', 'make', 'description_short')
    def _compute_display_name(self):
        for template in self:
            name = template.name
            if template.make:
                name = f"[{template.make}] {name}"
            if template.description_short:
                name = f"{name} - {template.description_short}"
            template.display_name = name

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.depends('name', 'make', 'description_short')
    def _compute_display_name(self):
        for product in self:
            name = product.name
            if product.make:
                name = f"[{product.make}] {name}"
            if product.description_short:
                name = f"{name} - {product.description_short}"
            product.display_name = name

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    make = fields.Char(
        related='product_id.make',
        string='Make',
        readonly=True
    )
    description_short = fields.Char(
        related='product_id.description_short',
        string='Short Desc',
        readonly=True
    )
