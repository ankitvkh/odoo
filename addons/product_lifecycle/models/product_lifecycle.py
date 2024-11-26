from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ProductLifecycle(models.Model):
    _name = 'product.lifecycle'
    _description = 'Product Lifecycle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(
        string='Reference',
        required=True,
        readonly=True,
        default=lambda self: _('New')
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('pending_approval', 'Pending Approval'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='draft', tracking=True, string='Status')

    # Stage fields - define current_stage_id first
    current_stage_id = fields.Many2one(
        'product.lifecycle.stage',
        string='Current Stage',
        tracking=True,
        readonly=True
    )

    # Now we can define fields that depend on current_stage_id
    allowed_stage_ids = fields.Many2many(
        'product.lifecycle.stage',
        compute='_compute_allowed_stages',
        string='Allowed Stages'
    )

    next_stage_id = fields.Many2one(
        'product.lifecycle.stage',
        string='Next Stage',
        compute='_compute_next_stage',
        store=True
    )

    requires_approval = fields.Boolean(
        string='Requires Approval',
        related='current_stage_id.approval_required',
        store=True,
        readonly=True
    )

    current_stage_approval_group_id = fields.Many2one(
        'res.groups',
        related='current_stage_id.approval_group_id',
        string='Current Stage Approval Group',
        store=True
    )

    approver_id = fields.Many2one(
        'res.users',
        string='Approver',
        tracking=True,
        domain="[('groups_id', 'in', current_stage_approval_group_id)]"
    )

    can_approve = fields.Boolean(
        string='Can Approve',
        compute='_compute_can_approve',
        store=True,
        help='Technical field to determine if current user can approve'
    )

    is_approver = fields.Boolean(
        string='Is Approver',
        compute='_compute_is_approver',
        store=True
    )

    # Other basic fields
    active = fields.Boolean(default=True, tracking=True)

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        tracking=True
    )

    product_id = fields.Many2one(
        'product.template',
        string='Product',
        required=True,
        tracking=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]"
    )

    start_date = fields.Date(
        string='Start Date',
        tracking=True
    )

    planned_end_date = fields.Date(
        string='Planned End Date',
        tracking=True
    )

    actual_end_date = fields.Date(
        string='Actual End Date',
        readonly=True,
        tracking=True
    )

    responsible_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        required=True,
        tracking=True
    )

    # Related records
    stage_history_ids = fields.One2many(
        'product.lifecycle.history',
        'lifecycle_id',
        string='Stage History'
    )

    attachment_ids = fields.One2many(
        'ir.attachment',
        'res_id',
        domain=[('res_model', '=', 'product.lifecycle')],
        string='Attachments'
    )

    can_move_to_next = fields.Boolean(
        string='Can Move to Next Stage',
        compute='_compute_can_move_to_next',
        store=True,
        help='Technical field to control Next Stage button visibility'
    )

    show_move_button = fields.Boolean(
        string='Show Move Button',
        compute='_compute_show_move_button'
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('product.lifecycle') or _('New')
        return super().create(vals_list)

    def action_start(self):
        """Start the lifecycle process"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Lifecycle can only be started from draft state.'))

        initial_stage = self.env['product.lifecycle.stage'].search([
            ('is_initial', '=', True)
        ], limit=1)

        if not initial_stage:
            raise UserError(_('No initial stage defined in the system.'))

        self.write({
            'state': 'in_progress',
            'current_stage_id': initial_stage.id,
            'start_date': fields.Date.today()
        })

        self._create_stage_history(initial_stage, None)
        return True

    def action_complete(self):
        """Complete the lifecycle"""
        self.ensure_one()
        if self.state != 'in_progress':
            raise UserError(_('Only in-progress lifecycles can be completed.'))

        if not self.current_stage_id.is_final:
            raise UserError(_('Cannot complete lifecycle: current stage is not marked as final.'))

        self.write({
            'state': 'completed',
            'actual_end_date': fields.Date.today()
        })
        return True

    def action_cancel(self):
        """Cancel the lifecycle"""
        self.ensure_one()
        if self.state in ['completed', 'cancelled']:
            raise UserError(_('Cannot cancel a completed or already cancelled lifecycle.'))

        self.write({'state': 'cancelled'})
        self.message_post(body=_('Lifecycle cancelled'), message_type='notification')
        return True

    def _create_stage_history(self, new_stage, old_stage=None):
        """Create a history record for stage change"""
        self.ensure_one()

        history_vals = {
            'lifecycle_id': self.id,
            'stage_id': new_stage.id,
            'previous_stage_id': old_stage and old_stage.id or False,
            'date': fields.Datetime.now(),
            'user_id': self.env.user.id,
            'notes': not old_stage and f'Started at {new_stage.name}' or f'Moved from {old_stage.name} to {new_stage.name}'
        }

        return self.env['product.lifecycle.history'].create(history_vals)

    @api.depends('current_stage_id', 'state')
    def _compute_allowed_stages(self):
        for record in self:
            if record.state == 'in_progress' and record.current_stage_id:
                record.allowed_stage_ids = record.current_stage_id.allowed_next_stages
            else:
                record.allowed_stage_ids = False

    @api.depends('state', 'current_stage_id')
    def _compute_next_stage(self):
        """Compute the next stage"""
        for record in self:
            if record.state == 'in_progress' and record.current_stage_id:
                next_stages = record.current_stage_id.allowed_next_stages
                record.next_stage_id = next_stages and next_stages[0].id or False
            else:
                record.next_stage_id = False

    @api.depends('state', 'approver_id')
    def _compute_is_approver(self):
        for record in self:
            record.is_approver = (
                record.state == 'pending_approval' and
                record.approver_id.id == self.env.user.id
            )

    @api.depends('state', 'approver_id')
    def _compute_can_approve(self):
        for record in self:
            record.can_approve = (
                record.state == 'pending_approval' and
                record.approver_id.id == self.env.user.id
            )

    def action_move_to_next_stage(self):
        self.ensure_one()
        if not self.show_move_button:
            raise UserError(_('Cannot move to next stage at this time.'))

        if not self.next_stage_id:
            raise UserError(_('No next stage defined.'))

        if self.next_stage_id.approval_required and not self.approver_id:
            raise UserError(_('Please select an approver before moving to the next stage.'))

        old_stage = self.current_stage_id

        if self.next_stage_id.approval_required:
            # Move to pending approval state
            vals = {
                'state': 'pending_approval',
            }
        else:
            # Direct movement to next stage
            vals = {
                'state': 'in_progress',
                'current_stage_id': self.next_stage_id.id,
            }

        self.write(vals)

        # Create history record
        self._create_stage_history(self.next_stage_id, old_stage)

        if self.next_stage_id.approval_required:
            # Create activity for approver
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=self.approver_id.id,
                note=f'Please review and approve {self.name} to move to next stage',
                summary='Approval Required'
            )

            # Notify approver
            self.message_post(
                body=_('Sent for approval to %s') % self.approver_id.name,
                message_type='notification'
            )

        return True

    @api.onchange('approver_id')
    def _onchange_approver(self):
        """Update can_move_to_next when approver changes"""
        self._compute_can_move_to_next()


    def action_approve(self):
        self.ensure_one()
        if not self.can_approve:
            raise UserError(_('You are not authorized to approve this stage.'))

        old_stage = self.current_stage_id
        next_stage = self.next_stage_id

        self.write({
            'state': 'in_progress',
            'current_stage_id': next_stage.id,
            'next_stage_id': False,
            'approver_id': False
        })

        self._create_stage_history(next_stage, old_stage)
        self.message_post(
            body=_('Stage approved by %s') % self.env.user.name,
            message_type='notification'
        )

        activities = self.activity_ids.filtered(lambda a: a.user_id == self.env.user)
        activities.action_done()

        return True

    def action_reject(self):
        self.ensure_one()
        if not self.can_approve:
            raise UserError(_('You are not authorized to reject this stage.'))

        old_stage = self.current_stage_id

        self.write({
            'state': 'in_progress',
            'next_stage_id': False,
            'approver_id': False
        })

        self._create_stage_history(old_stage, self.next_stage_id)
        self.message_post(
            body=_('Stage rejected by %s') % self.env.user.name,
            message_type='notification'
        )

        self.activity_schedule(
            'mail.mail_activity_data_todo',
            user_id=self.responsible_id.id,
            note=_('Your request was rejected by %s. Please review and update.') % self.env.user.name,
            summary='Stage Rejected'
        )

        activities = self.activity_ids.filtered(lambda a: a.user_id == self.env.user)
        activities.action_done()

        return True

    @api.depends('state', 'approver_id', 'next_stage_id', 'requires_approval')
    def _compute_can_move_to_next(self):
        for record in self:
            record.can_move_to_next = (
                    record.state == 'in_progress' and
                    record.next_stage_id and
                    (not record.requires_approval or
                     (record.requires_approval and record.approver_id))
            )

    @api.depends('state', 'current_stage_id', 'next_stage_id', 'approver_id', 'requires_approval')
    def _compute_show_move_button(self):
        """Compute whether to show the Move to Next Stage button"""
        for record in self:
            record.show_move_button = (
                    record.state == 'in_progress'
                    and record.next_stage_id
                    and (
                            not record.requires_approval
                            or (record.requires_approval and record.approver_id)
                    )
            )