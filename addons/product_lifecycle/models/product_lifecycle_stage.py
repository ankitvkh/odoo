# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductLifecycleStage(models.Model):
    _name = 'product.lifecycle.stage'
    _description = 'Product Lifecycle Stage'
    _order = 'sequence, id'

    name = fields.Char(
        string='Stage Name',
        required=True,
        translate=True
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Used to order stages. Lower is better."
    )
    description = fields.Html(
        string='Description',
        translate=True,
        help="Describe the purpose and requirements of this stage"
    )
    is_initial = fields.Boolean(
        string='Initial Stage',
        help="This stage is automatically applied when starting the lifecycle"
    )
    is_final = fields.Boolean(
        string='Final Stage',
        help="This stage marks the end of the lifecycle"
    )
    allowed_next_stages = fields.Many2many(
        'product.lifecycle.stage',
        'product_stage_next_rel',
        'from_stage_id',
        'to_stage_id',
        string='Allowed Next Stages',
        help="Stages that can follow this one"
    )
    required_document_types = fields.Char(
        string='Required Document Types',
        help="Comma-separated list of required document types (e.g., 'Drawing,Specification,Test Report')"
    )
    approval_required = fields.Boolean(
        string='Requires Approval',
        help="If checked, stage transition requires approval"
    )
    approval_group_id = fields.Many2one(
        'res.groups',
        string='Approval Group',
        help="User group that can approve transitions from this stage"
    )
    fold = fields.Boolean('Folded in Kanban', default=False)

    @api.constrains('is_initial')
    def _check_initial_stage(self):
        for stage in self:
            if stage.is_initial and self.search_count([
                ('is_initial', '=', True),
                ('id', '!=', stage.id)
            ]):
                raise ValidationError(_("Only one stage can be marked as initial."))

    @api.constrains('allowed_next_stages')
    def _check_next_stages(self):
        for stage in self:
            if stage.is_final and stage.allowed_next_stages:
                raise ValidationError(_("Final stages cannot have next stages."))