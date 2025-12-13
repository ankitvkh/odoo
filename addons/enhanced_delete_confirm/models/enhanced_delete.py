# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class EnhancedDeleteWizard(models.TransientModel):
    _name = 'enhanced.delete.confirm.wizard'
    _description = 'Enhanced Delete Confirmation Wizard'

    record_ids = fields.Char(string='Record IDs')
    model_name = fields.Char(string='Model Name')
    message = fields.Text(string='Message', readonly=True)
    linked_info = fields.Text(string='Linked Records', readonly=True)
    can_delete = fields.Boolean(string='Can Delete', default=True)

    @api.model
    def create_wizard(self, record_ids, model_name):
        """Create wizard for delete confirmation"""
        records = self.env[model_name].browse(record_ids)

        # Check for linked records
        linked_info = self._check_linked_records(records, model_name)
        can_delete = len(linked_info) == 0

        message = f"You are about to delete {len(records)} record(s)."
        if not can_delete:
            message += "\n\n⚠️ Warning: Some records have linked data that will also be deleted!"
        message += "\n\nThis action cannot be undone. Are you sure?"

        return self.create({
            'record_ids': ','.join(map(str, record_ids)),
            'model_name': model_name,
            'message': message,
            'linked_info': linked_info,
            'can_delete': can_delete,
        })

    def _check_linked_records(self, records, model_name):
        """Check for records that would be affected by deletion"""
        linked_messages = []

        # Common relationships to check
        checks = {
            'res.company': [
                ('res.users', 'company_id', 'Users'),
                ('res.partner', 'company_id', 'Contacts'),
            ],
            'res.partner': [
                ('res.users', 'partner_id', 'Users'),
                ('sale.order', 'partner_id', 'Sales Orders'),
                ('purchase.order', 'partner_id', 'Purchase Orders'),
            ],
            'product.product': [
                ('sale.order.line', 'product_id', 'Sales Order Lines'),
                ('purchase.order.line', 'product_id', 'Purchase Order Lines'),
                ('stock.move', 'product_id', 'Stock Moves'),
            ],
        }

        if model_name in checks:
            for related_model, field_name, display_name in checks[model_name]:
                try:
                    # Find linked records
                    linked_records = self.env[related_model].search([(field_name, 'in', records.ids)])
                    if linked_records:
                        linked_messages.append(f"• {len(linked_records)} {display_name}")
                except:
                    continue

        return "\n".join(linked_messages) if linked_messages else ""

    def action_delete(self):
        """Perform the delete action"""
        record_ids = [int(x) for x in self.record_ids.split(',') if x]
        records = self.env[self.model_name].browse(record_ids)

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

    def action_cancel(self):
        """Cancel the delete action"""
        return {'type': 'ir.actions.act_window_close'}