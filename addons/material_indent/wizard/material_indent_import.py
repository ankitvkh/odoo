# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import base64
import csv
import io
import logging

_logger = logging.getLogger(__name__)

class MaterialIndentImportWizard(models.TransientModel):
    _name = 'material.indent.import.wizard'
    _description = 'Import Material Indent Data'

    file = fields.Binary('CSV File', required=True)
    filename = fields.Char('Filename')

    def action_import_indent(self):
        """Parse CSV and create material indent with BOM data"""
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

            # Initialize variables
            Product = self.env['product.product']
            boms_to_create = {}
            current_product = None
            bom_data = None

            for row in rows:
                product = row.get('Product')
                project = row.get('Project')
                components_string = row.get('BOM Lines/Component')
                bom_key = f"{product}_{project}"  # Unique key for product + project combination
                
                # Skip empty rows
                if not components_string:
                    continue

                # If this is a new product+project combination
                if bom_key not in boms_to_create:
                    # Create or find the product
                    main_product = Product.search([('default_code', '=', product)], limit=1)
                    if not main_product:
                        main_product = Product.create({
                            'name': product,
                            'default_code': product,
                            'type': 'product',
                            'detailed_type': 'product',
                        })
                    
                    # Start new BOM data
                    boms_to_create[bom_key] = {
                        'product': main_product,
                        'components': [],
                        'project': project,
                        'flow_type': row.get('Flow Type'),
                        'bom_type': row.get('BOM Type'),
                    }

                # Get quantity for this row
                try:
                    quantity = float(row.get('Lines/Quantity', 1.0))
                except (ValueError, TypeError):
                    quantity = 1.0

                current_bom = boms_to_create[bom_key]

                # Process component (single component per row)
                comp_name = components_string.strip()
                if comp_name:
                    # Create or find component product
                    component = Product.search([('default_code', '=', comp_name)], limit=1)
                    if not component:
                        component = Product.create({
                            'name': comp_name,
                            'default_code': comp_name,
                            'type': 'product',
                            'detailed_type': 'product',
                        })

                    # Add component if not already in the BOM
                    component_data = {
                        'product_id': component.id,
                        'product_qty': quantity,
                        'product_uom_id': component.uom_id.id,
                    }

                    # Check for duplicate components
                    if not any(c['product_id'] == component.id for c in current_bom['components']):
                        current_bom['components'].append(component_data)

            if not boms_to_create:
                raise ValidationError(_('No valid BOMs found in the CSV file'))

            # Create BOMs and Material Indents
            MrpBom = self.env['mrp.bom']
            MaterialIndent = self.env['material.indent']
            created_indents = []

            for bom_key, bom_data in boms_to_create.items():
                # Create BOM first
                bom_vals = {
                    'product_tmpl_id': bom_data['product'].product_tmpl_id.id,
                    'product_qty': 1.0,
                    'type': 'normal',
                    'bom_line_ids': [(0, 0, comp) for comp in bom_data['components']],
                    'project_reference': bom_data['project'],
                    'bom_flow_type': 'project' if bom_data['flow_type'] == 'Project' else 'spare',
                }
                
                bom = MrpBom.create(bom_vals)

                # Create Material Indent
                indent = MaterialIndent.create({
                    'bom_id': bom.id,
                    'project_id': False,  # You might want to link to actual project
                    'state': 'draft',
                })
                
                # Load BOM components into indent
                indent.action_load_from_bom()
                created_indents.append(indent.id)

            # If only one indent was created, open it in form view
            if len(created_indents) == 1:
                return {
                    'name': _('Material Indent'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'material.indent',
                    'res_id': created_indents[0],
                    'view_mode': 'form',
                    'target': 'current',
                }
            # If multiple indents were created, show them in list view
            else:
                return {
                    'name': _('Created Material Indents'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'material.indent',
                    'domain': [('id', 'in', created_indents)],
                    'view_mode': 'tree,form',
                    'target': 'current',
                }

        except Exception as e:
            raise ValidationError(_(f'Error processing CSV: {str(e)}'))