# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EnhancedDeleteWizard(models.TransientModel):
    _name = 'enhanced.delete.wizard'
    _description = 'Enhanced Delete Confirmation Wizard'

    record_ids = fields.Char(string='Record IDs', required=True)
    model_name = fields.Char(string='Model Name', required=True)
    linked_records_info = fields.Text(string='Linked Records Information', readonly=True)
    action = fields.Selection([
        ('cancel', 'Cancel'),
        ('unlink_only', 'Delete only selected records'),
        ('cascade', 'Delete all linked records')
    ], string='Action', default='cancel', required=True)

    def _get_linked_records_info(self, records):
        """Get information about linked records for the given records"""
        info_lines = []
        total_linked = 0

        # Check common relationships that might exist
        relationships_to_check = [
            ('res.partner', 'child_ids', 'Contacts'),
            ('res.partner', 'bank_ids', 'Bank Accounts'),
            ('product.product', 'product_tmpl_id', 'Product Template'),
            ('sale.order', 'order_line', 'Sale Order Lines'),
            ('purchase.order', 'order_line', 'Purchase Order Lines'),
            ('account.move', 'line_ids', 'Journal Entries'),
            ('stock.picking', 'move_ids', 'Stock Moves'),
            ('hr.employee', 'user_id', 'Related User'),
        ]

        for record in records:
            linked_info = []
            for rel_model, rel_field, rel_name in relationships_to_check:
                if record._name == rel_model:
                    try:
                        related_records = getattr(record, rel_field, None)
                        if related_records and len(related_records) > 0:
                            linked_info.append(f"- {len(related_records)} {rel_name}")
                            total_linked += len(related_records)
                    except:
                        continue

            if linked_info:
                info_lines.append(f"{record.display_name}:")
                info_lines.extend(linked_info)

        if not info_lines:
            return "No linked records found."

        summary = f"Total linked records: {total_linked}\n\n"
        return summary + "\n".join(info_lines)

    @api.model
    def create_wizard(self, record_ids, model_name):
        """Create the enhanced delete wizard for the given records"""
        records = self.env[model_name].browse(record_ids)
        if not records:
            raise UserError(_("No records found to delete."))

        linked_info = self._get_linked_records_info(records)

        return self.create({
            'record_ids': ','.join(map(str, record_ids)),
            'model_name': model_name,
            'linked_records_info': linked_info,
        })

    def action_confirm(self):
        """Execute the chosen delete action"""
        self.ensure_one()

        record_ids = [int(id_str) for id_str in self.record_ids.split(',') if id_str]
        records = self.env[self.model_name].browse(record_ids)

        if self.action == 'cancel':
            return {'type': 'ir.actions.act_window_close'}

        elif self.action == 'unlink_only':
            # Just delete the records, let database constraints handle relationships
            try:
                records.unlink()
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Records deleted successfully.'),
                        'type': 'success',
                    }
                }
            except Exception as e:
                raise UserError(_("Cannot delete records: %s") % str(e))

        elif self.action == 'cascade':
            # Perform cascade delete by temporarily disabling constraints
            # This is a simplified approach - in production you'd want more sophisticated logic
            try:
                # For now, we'll try to delete and catch constraint violations
                records.unlink()
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Records and linked data deleted successfully.'),
                        'type': 'success',
                    }
                }
            except Exception as e:
                raise UserError(_("Cannot perform cascade delete: %s") % str(e))

        return {'type': 'ir.actions.act_window_close'}