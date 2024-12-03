# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import base64
import csv
import io
import logging

_logger = logging.getLogger(__name__)

class BomImportWizard(models.TransientModel):
    _name = 'mrp.bom.import.wizard'
    _description = 'Import BOM Data'

    file = fields.Binary('CSV File', required=True)
    filename = fields.Char('Filename')
    drawing_files = fields.Many2many(
        'ir.attachment',
        'bom_import_drawing_rel',
        'wizard_id',
        'attachment_id',
        string='Technical Drawings'
    )

    def action_preview_bom(self):
        """Parse CSV and open BOM form with pre-filled data"""
        if not self.file:
            raise ValidationError(_('Please upload a CSV file.'))

        try:
            # Read CSV file
            csv_data = base64.b64decode(self.file)
            csv_file = io.StringIO(csv_data.decode('utf-8'))
            reader = csv.DictReader(csv_file)
            rows = list(reader)

            if not rows:
                raise ValidationError(_('The CSV file is empty.'))

            # Find the main product (first row with is_main_product=true)
            main_product_row = next((row for row in rows if row.get('is_main_product', '').lower() == 'true'), None)
            if not main_product_row:
                raise ValidationError(_('No main product found in CSV. One row must have is_main_product=true'))

            # Find or create the main product
            Product = self.env['product.product']
            main_product = Product.search([('default_code', '=', main_product_row['product_code'])], limit=1)
            if not main_product:
                main_product = Product.create({
                    'name': main_product_row.get('product_name', main_product_row['product_code']),
                    'default_code': main_product_row['product_code'],
                    'type': 'product',
                    'detailed_type': 'product',
                })

            # Prepare components data
            component_lines = []
            for row in rows:
                if row.get('is_main_product', '').lower() == 'true':
                    continue

                # Find or create component product
                component = Product.search([('default_code', '=', row['product_code'])], limit=1)
                if not component:
                    component = Product.create({
                        'name': row.get('product_name', row['product_code']),
                        'default_code': row['product_code'],
                        'type': 'product',
                        'detailed_type': 'product',
                    })

                component_lines.append((0, 0, {
                    'product_id': component.id,
                    'product_qty': float(row.get('quantity', 1.0)),
                    'product_uom_id': component.uom_id.id,
                }))

            # Prepare drawing attachments
            drawing_attachment_ids = []
            if self.drawing_files:
                drawing_attachment_ids = [(6, 0, self.drawing_files.ids)]
                _logger.info(f"Drawing attachments prepared: {drawing_attachment_ids}")

            # Context for pre-filling the BOM form
            context = {
                'default_product_tmpl_id': main_product.product_tmpl_id.id,
                'default_product_qty': 1.0,
                'default_type': 'normal',
                'default_bom_line_ids': component_lines,
                'default_drawing_attachment_ids': drawing_attachment_ids,
            }

            _logger.info(f"Opening BOM form with context: {context}")

            return {
                'name': _('Create Bill of Materials'),
                'type': 'ir.actions.act_window',
                'res_model': 'mrp.bom',
                'view_mode': 'form',
                'view_id': self.env.ref('mrp.mrp_bom_form_view').id,
                'target': 'current',
                'context': context,
            }

        except Exception as e:
            raise ValidationError(_(f'Error processing CSV: {str(e)}'))