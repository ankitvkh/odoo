from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ProductLifecycle(models.Model):
    _name = 'product.lifecycle'
    _description = 'Product Lifecycle'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Reference',
        required=True,
        readonly=True,
        default=lambda self: _('New')
    )
    active = fields.Boolean(
        default=True,
        tracking=True
    )
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
    current_stage_id = fields.Many2one(
        'product.lifecycle.stage',
        string='Current Stage',
        tracking=True
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
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('pending_approval', 'Pending Approval'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='draft', tracking=True, string='Status')

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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].with_company(
                    vals.get('company_id') or self.env.company.id
                ).next_by_code('product.lifecycle') or _('New')
            if not vals.get('company_id'):
                vals['company_id'] = self.env.company.id
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
        self._create_stage_history(initial_stage)
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

        self.write({
            'state': 'cancelled'
        })
        return True

    def _create_stage_history(self, stage):
        """Create a history record for stage change"""
        return self.env['product.lifecycle.history'].create({
            'lifecycle_id': self.id,
            'stage_id': stage.id,
            'date': fields.Datetime.now(),
            'user_id': self.env.user.id,
        })

    def action_change_stage(self, new_stage_id):
        """Change current stage"""
        self.ensure_one()
        if self.state != 'in_progress':
            raise UserError(_('Can only change stage when lifecycle is in progress.'))

        new_stage = self.env['product.lifecycle.stage'].browse(new_stage_id)

        if new_stage not in self.current_stage_id.allowed_next_stages:
            raise UserError(_('Invalid stage transition. Please select from the allowed next stages.'))

        # Check required documents if any
        if new_stage.required_document_types:
            required_types = [t.strip() for t in new_stage.required_document_types.split(',')]
            missing_types = []
            for req_type in required_types:
                if not self.attachment_ids.filtered(lambda x: x.document_type == req_type):
                    missing_types.append(req_type)
            if missing_types:
                raise UserError(_('Missing required documents of type: %s') % ', '.join(missing_types))

        self.write({'current_stage_id': new_stage.id})
        self._create_stage_history(new_stage)
        return True

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'company_id' not in res:
            res['company_id'] = self.env.company.id
        return res

    allowed_stage_ids = fields.Many2many(
        'product.lifecycle.stage',
        compute='_compute_allowed_stages',
        string='Allowed Stages'
    )

    @api.depends('current_stage_id', 'state')
    def _compute_allowed_stages(self):
        for record in self:
            if record.state == 'in_progress' and record.current_stage_id:
                record.allowed_stage_ids = record.current_stage_id.allowed_next_stages
            else:
                record.allowed_stage_ids = False

    @api.onchange('current_stage_id')
    def _onchange_current_stage_id(self):
        if self.current_stage_id and self.current_stage_id in self.allowed_stage_ids:
            self.action_change_stage(self.current_stage_id.id)

    def action_change_stage(self, new_stage_id):
        self.ensure_one()
        new_stage = self.env['product.lifecycle.stage'].browse(new_stage_id)

        if new_stage not in self.current_stage_id.allowed_next_stages:
            raise UserError(_('Invalid stage transition.'))

        # Check required documents
        if new_stage.required_document_types:
            required_types = [t.strip() for t in new_stage.required_document_types.split(',')]
            existing_types = self.attachment_ids.mapped('document_type')
            missing_types = [t for t in required_types if t not in existing_types]
            if missing_types:
                raise UserError(_('Missing required documents of type: %s') % ', '.join(missing_types))

        # Handle approval if required
        if new_stage.approval_required:
            if not new_stage.approval_group_id:
                raise ValidationError(_('Approval group must be defined for stages requiring approval.'))

            if new_stage.approval_group_id not in self.env.user.groups_id:
                self.write({'state': 'pending_approval'})
                return True

        self.write({'current_stage_id': new_stage.id})
        self._create_stage_history(new_stage)
        return True