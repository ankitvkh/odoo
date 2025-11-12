# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class LocationMaster(models.Model):
    _name = 'location.master'
    _description = 'Location Master'
    _order = 'code'
    _parent_name = 'parent_id'
    _parent_store = True
    
    code = fields.Char(
        string='Location Code',
        required=True,
        index=True,
        help='Unique code for the location (e.g., MUM, DEL)'
    )
    name = fields.Char(
        string='Location Name',
        required=True,
        help='Full name of the location'
    )
    parent_id = fields.Many2one(
        'location.master',
        string='Parent Location',
        index=True,
        ondelete='restrict',
        help='Parent location in the hierarchy'
    )
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many(
        'location.master',
        'parent_id',
        string='Child Locations'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        help='Company this location belongs to'
    )
    address = fields.Text(
        string='Address',
        help='Full address of the location'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Uncheck to archive the location'
    )
    user_ids = fields.One2many(
        'res.users',
        'location_id',
        string='Users',
        help='Users assigned to this location'
    )
    user_count = fields.Integer(
        string='User Count',
        compute='_compute_user_count',
        store=True
    )
    
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Location code must be unique!'),
    ]
    
    @api.depends('user_ids')
    def _compute_user_count(self):
        """Compute the number of users assigned to this location"""
        for location in self:
            location.user_count = len(location.user_ids)
    
    @api.constrains('parent_id')
    def _check_recursion(self):
        """Prevent circular parent-child relationships"""
        if not self._check_recursion():
            raise ValidationError(_('Error! You cannot create recursive location hierarchies.'))
    
    @api.constrains('code')
    def _check_code_format(self):
        """Validate location code format"""
        for location in self:
            if location.code and not location.code.replace('_', '').replace('-', '').isalnum():
                raise ValidationError(_('Location code must be alphanumeric (underscores and hyphens allowed).'))
    
    def name_get(self):
        """Display code and name together"""
        result = []
        for location in self:
            name = f"[{location.code}] {location.name}"
            result.append((location.id, name))
        return result
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """Search by code or name"""
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', operator, name), ('name', operator, name)]
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
    
    def get_location_hierarchy(self):
        """
        Return all child locations for filtering
        Returns a list of location IDs including self and all descendants
        """
        self.ensure_one()
        child_locations = self.search([('id', 'child_of', self.id)])
        return child_locations.ids
    
    def action_view_users(self):
        """Action to view users assigned to this location"""
        self.ensure_one()
        return {
            'name': _('Users at %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'view_mode': 'tree,form',
            'domain': [('location_id', '=', self.id)],
            'context': {'default_location_id': self.id},
        }
    
    @api.ondelete(at_uninstall=False)
    def _unlink_except_with_users(self):
        """Prevent deletion of locations with assigned users"""
        for location in self:
            if location.user_ids:
                raise ValidationError(
                    _('Cannot delete location "%s" because it has %d assigned user(s). '
                      'Please reassign the users first.') % (location.name, len(location.user_ids))
                )
