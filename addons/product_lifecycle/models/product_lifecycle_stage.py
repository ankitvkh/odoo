from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProductLifecycleStage(models.Model):
    _name = 'product.lifecycle.stage'
    _description = 'Product Lifecycle Stage'
    _order = 'sequence, id'

    name = fields.Char('Stage Name', required=True)
    description = fields.Text('Description')
    sequence = fields.Integer('Sequence', default=10)
    fold = fields.Boolean(
        'Folded in Views',
        default=False,
        help="This stage is folded in the kanban/statusbar view when there are no records in that stage to display."
    )
    is_initial = fields.Boolean('Is Initial Stage', default=False)
    is_final = fields.Boolean('Is Final Stage', default=False)
    approval_required = fields.Boolean('Requires Approval', default=False)
    approval_group_id = fields.Many2one(
        'res.groups',
        string='Approval Group',
        help="User group that can approve transitions to this stage"
    )
    allowed_next_stages = fields.Many2many(
        'product.lifecycle.stage',
        'product_lifecycle_stage_next_rel',
        'from_stage_id',
        'to_stage_id',
        string='Allowed Next Stages'
    )
    required_document_types = fields.Char(
        'Required Document Types',
        help="Comma-separated list of required document types for this stage"
    )

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Stage name must be unique!')
    ]

    @api.constrains('is_initial')
    def _check_initial_stage(self):
        for stage in self:
            if stage.is_initial and self.search_count([
                ('is_initial', '=', True),
                ('id', '!=', stage.id)
            ]) > 0:
                raise ValidationError(_('Only one stage can be marked as initial stage.'))

    @api.constrains('required_document_types')
    def _check_document_types_format(self):
        for stage in self:
            if stage.required_document_types:
                types = [t.strip() for t in stage.required_document_types.split(',')]
                if not all(types):
                    raise ValidationError(_('Document types must be a valid comma-separated list.'))

    @api.constrains('is_final', 'allowed_next_stages')
    def _check_final_stage_next_stages(self):
        for stage in self:
            if stage.is_final and stage.allowed_next_stages:
                raise ValidationError(_('Final stages cannot have next stages.'))

    def action_move_to_next_stage(self):
        self.ensure_one()
        if not self.next_stage_id:
            raise UserError(_('No next stage defined.'))

        if self.next_stage_id.approval_required and not self.approver_id:
            raise UserError(_('Please select an approver before moving to the next stage.'))

        old_stage = self.current_stage_id

        if self.next_stage_id.approval_required:
            # Move to pending approval state
            self.write({
                'state': 'pending_approval'
            })

            # Create activity for approver
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=self.approver_id.id,
                note=f'Please review and approve {self.name} to move to next stage',
                summary='Approval Required'
            )

            # Record in history
            self._create_stage_history(self.next_stage_id, old_stage)

            # Notify approver
            self.message_post(
                body=_('Sent for approval to %s') % self.approver_id.name,
                message_type='notification'
            )
        else:
            # Direct movement to next stage
            self.write({
                'current_stage_id': self.next_stage_id.id,
                'state': 'in_progress'
            })

            # Record in history
            self._create_stage_history(self.next_stage_id, old_stage)

        return True

    @api.onchange('approver_id')
    def _onchange_approver(self):
        """Enable 'Move to Next Stage' when approver is selected"""
        if self.approver_id and self.state == 'in_progress':
            return {
                'warning': {
                    'title': _('Ready to Move'),
                    'message': _('You can now move this record to the next stage for approval.')
                }
            }