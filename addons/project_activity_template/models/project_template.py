# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProjectActivityTemplate(models.Model):
    _name = 'project.activity.template'
    _description = 'Project Activity Template'
    _order = 'sequence, id'
    _inherit = ['mail.thread']

    name = fields.Char(
        string='Template Name',
        required=True,
        tracking=True
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    description = fields.Html(
        string='Description',
        tracking=True
    )
    active = fields.Boolean(
        default=True,
        tracking=True
    )
    task_template_ids = fields.One2many(
        'project.task.template',
        'activity_template_id',
        string='Task Templates'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        tracking=True
    )
    task_count = fields.Integer(
        compute='_compute_task_count',
        string='Tasks'
    )

    @api.depends('task_template_ids')
    def _compute_task_count(self):
        for template in self:
            template.task_count = len(template.task_template_ids)

    def action_apply_template(self, project_id):
        self.ensure_one()
        project = self.env['project.project'].browse(project_id)
        if not project.exists():
            raise UserError(_("Project not found."))

        created_tasks = self.env['project.task']
        for task_template in self.task_template_ids:
            created_tasks |= task_template._create_task(project)

        return created_tasks


class ProjectTaskTemplate(models.Model):
    _name = 'project.task.template'
    _description = 'Project Task Template'
    _order = 'sequence, id'

    name = fields.Char(
        string='Task Name',
        required=True
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    description = fields.Html(
        string='Description'
    )
    activity_template_id = fields.Many2one(
        'project.activity.template',
        string='Activity Template',
        required=True,
        ondelete='cascade'
    )
    planned_hours = fields.Float(
        string='Initially Planned Hours',
        digits=(16, 2)
    )
    user_id = fields.Many2one(
        'res.users',
        string='Assigned To',
        default=lambda self: self.env.user
    )
    tag_ids = fields.Many2many(
        'project.tags',
        string='Tags'
    )
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Very High')
    ], default='1', string='Priority')

    # Dependencies
    depend_on_task_ids = fields.Many2many(
        'project.task.template',
        'project_task_template_dependency_rel',
        'task_id',
        'dependency_task_id',
        string='Dependencies',
        domain="[('activity_template_id', '=', activity_template_id), ('id', '!=', id)]"
    )

    @api.constrains('depend_on_task_ids')
    def _check_dependency_recursion(self):
        for task in self:
            if task.id in task._get_all_dependent_tasks():
                raise UserError(_("Circular dependencies are not allowed between tasks."))

    def _get_all_dependent_tasks(self, visited=None):
        if visited is None:
            visited = set()

        dependent_tasks = set()
        for task in self:
            if task.id in visited:
                continue
            visited.add(task.id)
            dependent_tasks.update(task.depend_on_task_ids.ids)
            for dep_task in task.depend_on_task_ids:
                dependent_tasks.update(dep_task._get_all_dependent_tasks(visited))
        return dependent_tasks

    def _create_task(self, project):
        self.ensure_one()
        vals = {
            'name': self.name,
            'project_id': project.id,
            'description': self.description,
            'planned_hours': self.planned_hours,
            'user_id': self.user_id.id,
            'tag_ids': [(6, 0, self.tag_ids.ids)],
            'priority': self.priority,
            'sequence': self.sequence,
        }
        task = self.env['project.task'].create(vals)
        return task


class Project(models.Model):
    _inherit = 'project.project'

    def action_apply_activity_template(self):
        self.ensure_one()
        return {
            'name': _('Apply Activity Template'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.apply.activity.template.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_project_id': self.id,
                'dialog_size': 'medium',
            },
        }


class ProjectApplyActivityTemplateWizard(models.TransientModel):
    _name = 'project.apply.activity.template.wizard'
    _description = 'Apply Activity Template Wizard'

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True
    )
    template_id = fields.Many2one(
        'project.activity.template',
        string='Activity Template',
        required=True,
        domain="[('company_id', 'in', [False, company_id])]"
    )
    company_id = fields.Many2one(
        related='project_id.company_id',
        string='Company',
        readonly=True
    )

    def action_apply(self):
        self.ensure_one()
        tasks = self.template_id.action_apply_template(self.project_id.id)
        return {
            'name': _('Created Tasks'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'list,form',
            'domain': [('id', 'in', tasks.ids)],
            'target': 'current',
            'context': {'create': False}
        }