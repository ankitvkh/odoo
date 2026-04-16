# -*- coding: utf-8 -*-

from odoo import models, fields

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
