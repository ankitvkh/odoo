# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    location_id = fields.Many2one(
        'location.master',
        string='Primary Location',
        help='Primary location assignment for this user',
        index=True
    )
    group_code = fields.Char(
        string='Group Code',
        related='location_id.code',
        store=False,
        readonly=True,
        help='Location code for record-level security filtering'
    )
    secondary_location_ids = fields.Many2many(
        'location.master',
        'res_users_location_master_rel',
        'res_users_id',
        'location_master_id',
        string='Secondary Locations',
        help='Additional locations this user can access'
    )
    department_ids = fields.Many2many(
        'hr.department',
        'res_users_hr_department_rel',
        'user_id',
        'department_id',
        string='Departments',
        help='Departments this user belongs to'
    )
    access_level = fields.Selection([
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('user', 'User'),
        ('viewer', 'Viewer'),
    ], string='Access Level', default='user', help='Quick access level indicator')
    
    @api.constrains('location_id', 'secondary_location_ids')
    def _check_location_company(self):
        """Ensure locations belong to the same company as the user"""
        for user in self:
            if user.company_id:
                all_locations = user.location_id | user.secondary_location_ids
                invalid_locations = all_locations.filtered(
                    lambda loc: loc.company_id and loc.company_id != user.company_id
                )
                if invalid_locations:
                    raise ValidationError(
                        _('Location(s) %s do not belong to the user\'s company.') % 
                        ', '.join(invalid_locations.mapped('name'))
                    )
    
    def get_accessible_locations(self):
        """
        Return list of all accessible location IDs for this user
        Includes primary location and all secondary locations with their hierarchies
        """
        self.ensure_one()
        
        # Admin users have access to all locations
        if self.has_group('base.group_system'):
            return self.env['location.master'].search([]).ids
        
        accessible_locations = self.env['location.master']
        
        # Add primary location and its hierarchy
        if self.location_id:
            accessible_locations |= self.env['location.master'].browse(
                self.location_id.get_location_hierarchy()
            )
        
        # Add secondary locations and their hierarchies
        for location in self.secondary_location_ids:
            accessible_locations |= self.env['location.master'].browse(
                location.get_location_hierarchy()
            )
        
        return accessible_locations.ids
    
    def has_location_access(self, location_id):
        """
        Check if user can access a specific location
        
        :param location_id: ID of the location to check
        :return: Boolean indicating access permission
        """
        self.ensure_one()
        
        # Admin users have access to all locations
        if self.has_group('base.group_system'):
            return True
        
        accessible_location_ids = self.get_accessible_locations()
        return location_id in accessible_location_ids
    
    def get_record_domain(self, location_field='location_id'):
        """
        Generate domain filter for location-based access
        
        :param location_field: Name of the location field in the target model
        :return: Domain list for filtering records
        """
        self.ensure_one()
        
        # Admin users see all records
        if self.has_group('base.group_system'):
            return []
        
        accessible_location_ids = self.get_accessible_locations()
        
        if not accessible_location_ids:
            # User has no location access, return empty domain
            return [(location_field, '=', False)]
        
        # Return domain that includes accessible locations or records without location
        return ['|', (location_field, 'in', accessible_location_ids), (location_field, '=', False)]
    
    @api.model
    def create(self, vals):
        """Override create to set default access level based on groups"""
        user = super(ResUsers, self).create(vals)
        user._update_access_level()
        return user
    
    def write(self, vals):
        """Override write to update access level when groups change"""
        result = super(ResUsers, self).write(vals)
        if 'groups_id' in vals:
            self._update_access_level()
        return result
    
    def _update_access_level(self):
        """Update access level based on assigned groups"""
        for user in self:
            if user.has_group('base.group_system'):
                user.access_level = 'admin'
            elif user.has_group('base.group_erp_manager'):
                user.access_level = 'manager'
            elif user.has_group('base.group_user'):
                user.access_level = 'user'
            else:
                user.access_level = 'viewer'
    
    def action_view_accessible_locations(self):
        """Action to view all accessible locations for this user"""
        self.ensure_one()
        accessible_location_ids = self.get_accessible_locations()
        return {
            'name': _('Accessible Locations for %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'location.master',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', accessible_location_ids)],
        }
