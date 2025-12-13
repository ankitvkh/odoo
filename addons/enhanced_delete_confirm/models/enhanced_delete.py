# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import SQL


class EnhancedDeleteWizard(models.TransientModel):
    _name = 'enhanced.delete.confirm.wizard'
    _description = 'Enhanced Delete Confirmation Wizard'

    record_ids = fields.Char(string='Record IDs')
    model_name = fields.Char(string='Model Name')
    message = fields.Html(string='Message', readonly=True)
    linked_info = fields.Html(string='Linked Records', readonly=True)
    has_linked_records = fields.Boolean(string='Has Linked Records', default=False)
    delete_mode = fields.Selection([
        ('unlink_only', 'Unlink and Delete Selected Records Only'),
        ('cascade', 'Delete Everything (Cascade Delete)')
    ], string='Delete Mode', default='unlink_only')

    @api.model
    def create_wizard(self, record_ids, model_name):
        """Create wizard for delete confirmation"""
        # Check if enhanced delete is enabled
        if not self.env['ir.config_parameter'].sudo().get_param('enhanced_delete_confirm.enabled', 'True') == 'True':
            return False
        
        # Check minimum records threshold
        min_records = int(self.env['ir.config_parameter'].sudo().get_param('enhanced_delete_confirm.min_records', '1'))
        if len(record_ids) < min_records:
            return False
        
        # Check if model is excluded
        excluded_models = self.env['ir.config_parameter'].sudo().get_param('enhanced_delete_confirm.excluded_models', '')
        if excluded_models:
            excluded_list = [m.strip() for m in excluded_models.split(',')]
            if model_name in excluded_list:
                return False
        
        records = self.env[model_name].browse(record_ids)

        # Check for linked records
        linked_data = self._check_linked_records(records, model_name)
        has_linked = bool(linked_data['details'])

        # Build message
        message = f"<p><strong>You are about to delete {len(records)} record(s) from {model_name}</strong></p>"
        
        if has_linked:
            message += """
            <div class="alert alert-warning">
                <i class="fa fa-warning"></i> 
                <strong>Warning:</strong> These records have linked data!
            </div>
            """
        
        message += "<p>Choose how you want to proceed:</p>"
        message += "<ul>"
        message += "<li><strong>Unlink Only:</strong> Remove relationships and delete only selected records</li>"
        message += "<li><strong>Cascade Delete:</strong> Delete selected records AND all linked data</li>"
        message += "</ul>"

        # Build linked info HTML
        linked_html = ""
        if linked_data['details']:
            linked_html = "<div><strong>Linked Records Found:</strong><ul>"
            for detail in linked_data['details']:
                linked_html += f"<li>{detail}</li>"
            linked_html += "</ul></div>"
        else:
            linked_html = "<p>No linked records found. Safe to delete.</p>"

        return self.create({
            'record_ids': ','.join(map(str, record_ids)),
            'model_name': model_name,
            'message': message,
            'linked_info': linked_html,
            'has_linked_records': has_linked,
        })

    def _check_linked_records(self, records, model_name):
        """Check for records that would be affected by deletion"""
        details = []
        relationships = []

        try:
            model = self.env[model_name]
            
            # Get all fields that reference this model
            referring_fields = self.env['ir.model.fields'].search([
                ('relation', '=', model_name),
                ('ttype', 'in', ['many2one', 'one2many', 'many2many'])
            ])

            for field in referring_fields:
                try:
                    ref_model = self.env[field.model]
                    
                    # Build domain based on field type
                    if field.ttype == 'many2one':
                        domain = [(field.name, 'in', records.ids)]
                    elif field.ttype == 'one2many':
                        domain = [(field.name, 'in', records.ids)]
                    else:  # many2many
                        domain = [(field.name, 'in', records.ids)]
                    
                    linked_count = ref_model.search_count(domain)
                    
                    if linked_count > 0:
                        model_desc = ref_model._description or field.model
                        details.append(
                            f"<strong>{linked_count}</strong> {model_desc} "
                            f"(via {field.field_description or field.name})"
                        )
                        relationships.append({
                            'model': field.model,
                            'field': field.name,
                            'count': linked_count,
                            'ondelete': field.on_delete or 'set null'
                        })
                except Exception as e:
                    continue

        except Exception as e:
            details.append(f"Error checking relationships: {str(e)}")

        return {
            'details': details,
            'relationships': relationships
        }

    def action_delete(self):
        """Perform the delete action based on selected mode"""
        record_ids = [int(x) for x in self.record_ids.split(',') if x]
        records = self.env[self.model_name].browse(record_ids)

        try:
            if self.delete_mode == 'unlink_only':
                # Unlink relationships first
                self._unlink_relationships(records)
            
            # Now delete the records (cascade or after unlinking)
            records.unlink()
            
            mode_text = "with linked data" if self.delete_mode == 'cascade' else "only"
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Records deleted successfully (%s).') % mode_text,
                    'type': 'success',
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }
        except Exception as e:
            raise UserError(_("Cannot delete records: %s") % str(e))

    def _unlink_relationships(self, records):
        """Unlink relationships before deleting records"""
        model_name = records._name
        
        # Get all fields that reference this model
        referring_fields = self.env['ir.model.fields'].search([
            ('relation', '=', model_name),
            ('ttype', 'in', ['many2one', 'one2many', 'many2many'])
        ])

        for field in referring_fields:
            try:
                ref_model = self.env[field.model]
                
                if field.ttype == 'many2one':
                    # Set many2one fields to False/None
                    domain = [(field.name, 'in', records.ids)]
                    linked_records = ref_model.search(domain)
                    if linked_records:
                        linked_records.write({field.name: False})
                        
                elif field.ttype == 'one2many':
                    # For one2many, we need to handle the inverse many2one
                    domain = [(field.name, 'in', records.ids)]
                    linked_records = ref_model.search(domain)
                    if linked_records:
                        # Get the inverse field name
                        inverse_field = field.relation_field
                        if inverse_field:
                            linked_records.write({inverse_field: False})
                        
                elif field.ttype == 'many2many':
                    # Unlink many2many relationships
                    domain = [(field.name, 'in', records.ids)]
                    linked_records = ref_model.search(domain)
                    if linked_records:
                        for linked_rec in linked_records:
                            linked_rec.write({field.name: [(3, rid) for rid in records.ids]})
                            
            except Exception as e:
                # Log but continue with other fields
                continue

    def action_cancel(self):
        """Cancel the delete action"""
        return {'type': 'ir.actions.act_window_close'}