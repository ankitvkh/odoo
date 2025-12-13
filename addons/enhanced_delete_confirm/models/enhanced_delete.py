# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class EnhancedDeleteWizard(models.TransientModel):
    _name = 'enhanced.delete.confirm.wizard'
    _description = 'Enhanced Delete Confirmation Wizard'

    record_ids = fields.Char(string='Record IDs')
    model_name = fields.Char(string='Model Name')
    message = fields.Text(string='Message', readonly=True)

    @api.model
    def create_wizard(self, record_ids, model_name):
        """Create wizard for delete confirmation"""
        records = self.env[model_name].browse(record_ids)
        message = f"You are about to delete {len(records)} record(s).\n\n"
        message += "This action cannot be undone. Are you sure?"

        return self.create({
            'record_ids': ','.join(map(str, record_ids)),
            'model_name': model_name,
            'message': message,
        })

    def action_delete(self):
        """Perform the delete action"""
        record_ids = [int(x) for x in self.record_ids.split(',') if x]
        records = self.env[self.model_name].browse(record_ids)
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

    def action_cancel(self):
        """Cancel the delete action"""
        return {'type': 'ir.actions.act_window_close'}