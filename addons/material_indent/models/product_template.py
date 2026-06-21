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

    @api.depends('name', 'make', 'description_short', 'default_code')
    def _compute_display_name(self):
        super()._compute_display_name()
        for template in self:
            name = template.display_name or template.name or ''
            if not name:
                continue
            if template.make:
                if template.default_code and name.startswith(f"[{template.default_code}]"):
                    prefix_len = len(template.default_code) + 2
                    name = f"[{template.default_code}] [{template.make}]{name[prefix_len:]}"
                else:
                    name = f"[{template.make}] {name}"
            if template.description_short:
                name = f"{name} - {template.description_short}"
            template.display_name = name

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.depends('name', 'make', 'description_short', 'default_code')
    def _compute_display_name(self):
        super()._compute_display_name()
        for product in self:
            name = product.display_name or product.name or ''
            if not name:
                continue
            if product.make:
                if product.default_code and name.startswith(f"[{product.default_code}]"):
                    prefix_len = len(product.default_code) + 2
                    name = f"[{product.default_code}] [{product.make}]{name[prefix_len:]}"
                else:
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
