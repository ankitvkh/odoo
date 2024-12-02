# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class ProjectTask(models.Model):
    _inherit = 'project.task'

    requires_upload = fields.Boolean(
        string='Requires Document Upload',
        help='Check this if the task requires a document upload to be completed',
        tracking=True
    )
    has_uploaded_file = fields.Boolean(
        string='Has Uploaded File',
        compute='_compute_has_uploaded_file',
        store=True,
        help='Indicates if this task has any documents attached'
    )
    escalation_email = fields.Char(
        string='Escalation Email',
        help='Additional email addresses for escalation (comma-separated)'
    )
    last_escalation_date = fields.Datetime(
        string='Last Escalation Date',
        copy=False,
        readonly=True
    )
    is_escalated = fields.Boolean(
        string='Is Escalated',
        compute='_compute_is_escalated',
        store=True
    )

    @api.depends('date_deadline', 'state')
    def _compute_is_escalated(self):
        for task in self:
            task.is_escalated = False
            if task.date_deadline and task.state not in ['1_done', '03_approved']:
                deadline_date = fields.Date.from_string(task.date_deadline)
                current_date = fields.Date.from_string(fields.Date.today())
                task.is_escalated = deadline_date < current_date
                _logger.info(f'Task {task.name}: Deadline: {deadline_date}, Today: {current_date}, Is Escalated: {task.is_escalated}')

    @api.depends('message_ids', 'message_ids.attachment_ids')
    def _compute_has_uploaded_file(self):
        for task in self:
            attachments = self.env['ir.attachment'].search_count([
                ('res_model', '=', 'project.task'),
                ('res_id', '=', task.id)
            ])
            task.has_uploaded_file = bool(attachments)
            _logger.info(f'Task {task.name}: Computing has_uploaded_file. Attachments found: {attachments}')

    def _validate_dependencies(self):
        """Check if all blocking tasks are completed"""
        self.ensure_one()
        blocking_tasks = self.depend_on_ids.filtered(
            lambda t: t.state != '1_done'
        )
        if blocking_tasks:
            raise ValidationError(_(
                'Cannot complete task "%(task)s" because it is blocked by:\n%(blocking_tasks)s',
                task=self.name,
                blocking_tasks='\n'.join(['- ' + t.name for t in blocking_tasks])
            ))

    def _validate_upload_requirement(self):
        """Check if required documents are uploaded"""
        self.ensure_one()
        if self.requires_upload and not self.has_uploaded_file:
            raise ValidationError(_(
                'Cannot complete task "%(task)s" because it requires a document upload.',
                task=self.name
            ))

    def write(self, vals):
        _logger.info(f'Write called with vals: {vals}')

        # Handle both stage and state changes
        if 'state' in vals or 'stage_id' in vals:
            for task in self:
                # Force recompute attachments
                task._compute_has_uploaded_file()

                # State change validations
                if 'state' in vals:
                    new_state = vals['state']
                    # Check for both done and approved states
                    if new_state in ['1_done', '03_approved']:
                        task._validate_dependencies()
                        task._validate_upload_requirement()

                # Stage change validations
                if 'stage_id' in vals:
                    new_stage = self.env['project.task.type'].browse(vals['stage_id'])
                    if new_stage.id != task.stage_id.id:  # Only validate if stage is actually changing
                        if task.stage_id and new_stage.sequence > task.stage_id.sequence:
                            task._validate_dependencies()
                            task._validate_upload_requirement()

        # Handle deadline changes for escalation
        if 'date_deadline' in vals:
            deadline = fields.Date.from_string(vals['date_deadline'])
            current_date = fields.Date.from_string(fields.Date.today())
            if deadline < current_date:
                self._send_escalation_email()

        return super().write(vals)

    def _send_escalation_email(self, is_reminder=False):
        """Send escalation email for overdue tasks"""
        for task in self:
            if not task.date_deadline:
                continue

            # Collect email recipients
            email_to = set()

            # Add project manager
            if task.project_id.user_id:
                email_to.add(task.project_id.user_id.email)

            # Add custom escalation emails
            if task.escalation_email:
                email_to.update(email.strip() for email in task.escalation_email.split(','))

            # Add assignees
            if task.user_ids:
                email_to.update(task.user_ids.mapped('email'))

            if not email_to:
                _logger.warning(f'No recipients found for task escalation: {task.name}')
                continue

            try:
                mail_values = {
                    'subject': f'{"REMINDER: " if is_reminder else ""}Task Overdue: {task.name}',
                    'body_html': f"""
                        <p>Hello,</p>
                        <p>This is to inform you that the following task is overdue:</p>
                        <ul>
                            <li><strong>Task:</strong> {task.name}</li>
                            <li><strong>Project:</strong> {task.project_id.name}</li>
                            <li><strong>Deadline:</strong> {task.date_deadline}</li>
                            <li><strong>Current Stage:</strong> {task.stage_id.name}</li>
                            <li><strong>Assigned to:</strong> {', '.join(task.user_ids.mapped('name'))}</li>
                        </ul>
                        <p>Please take necessary action to complete this task or update the deadline if needed.</p>
                        <p>Best regards,<br/>{self.env.company.name}</p>
                    """,
                    'email_to': ','.join(filter(None, email_to)),
                    'email_from': self.env.company.email or self.env.user.email,
                }

                self.env['mail.mail'].sudo().create(mail_values).send()
                task.last_escalation_date = fields.Datetime.now()
                _logger.info(f'Escalation email sent for task: {task.name}')

            except Exception as e:
                _logger.error(f'Failed to send escalation email for task {task.name}: {str(e)}')

    @api.model
    def _check_overdue_tasks(self):
        """Cron job to check for overdue tasks"""
        current_date = fields.Date.from_string(fields.Date.today())
        overdue_tasks = self.search([
            ('date_deadline', '<', fields.Date.today()),
            ('state', 'not in', ['1_done', '03_approved']),
        ])

        for task in overdue_tasks:
            if not task.last_escalation_date or \
                    task.last_escalation_date < fields.Datetime.now() - timedelta(days=1):
                task._send_escalation_email(is_reminder=bool(task.last_escalation_date))

    @api.constrains('state', 'stage_id')
    def _check_all_constraints(self):
        """Ensure all constraints are checked when relevant fields change"""
        for task in self:
            if task.state in ['1_done', '03_approved'] or \
                    (task.stage_id and task.stage_id == task.project_id.type_ids[-1]):
                task._validate_dependencies()
                task._validate_upload_requirement()

    def action_toggle_done(self):
        """Override to add validation before marking as done"""
        for task in self:
            task._validate_dependencies()
            task._validate_upload_requirement()
        return super().action_toggle_done()