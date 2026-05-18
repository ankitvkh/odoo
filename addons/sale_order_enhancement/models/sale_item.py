# -*- coding: utf-8 -*-

from odoo import models, fields

class SaleItem(models.Model):
    _name = 'sale.item'
    _description = 'Sales Custom Item'
    _rec_name = 'name'

    name = fields.Char(string='Item Name', required=True)
    make = fields.Char(string='Make')
    description_short = fields.Char(string='Short Description')
