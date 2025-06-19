from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # GST Treatment field with comprehensive options
    l10n_in_gst_treatment = fields.Selection([
        ('regular', 'Regular Business - Registered'),
        ('composition', 'Composition Scheme'),
        ('unregistered', 'Unregistered Business'),
        ('consumer', 'Consumer'),
        ('overseas', 'Overseas'),
        ('special_economic_zone', 'Special Economic Zone'),
        ('deemed_export', 'Deemed Export'),
        ('uin_holders', 'UIN Holders')
    ], string='GST Treatment',
       default='regular',
       help="GST treatment type for the partner as per Indian GST rules")

    # Separate GSTIN field for Indian GST number
    l10n_in_gstin = fields.Char(
        string='GSTIN',
        size=15,
        help="GST Identification Number of the partner"
    )

    # Field to store partner's GST state code
    l10n_in_state_code = fields.Char(
        string='State Code',
        size=2,
        compute='_compute_l10n_in_state_code',
        store=True,
        help="First two digits of GSTIN representing state code"
    )

    # PAN Number field
    l10n_in_pan = fields.Char(
        string='PAN',
        size=10,
        help="Permanent Account Number"
    )

    # Flag for GST registered entity
    l10n_in_is_gst_registered = fields.Boolean(
        string='Is GST Registered?',
        compute='_compute_l10n_in_is_gst_registered',
        store=True
    )

    @api.depends('l10n_in_gstin')
    def _compute_l10n_in_state_code(self):
        """Compute state code from GSTIN"""
        for partner in self:
            if partner.l10n_in_gstin and len(partner.l10n_in_gstin) >= 2:
                partner.l10n_in_state_code = partner.l10n_in_gstin[:2]
            else:
                partner.l10n_in_state_code = False

    @api.depends('l10n_in_gst_treatment', 'l10n_in_gstin')
    def _compute_l10n_in_is_gst_registered(self):
        """Compute whether partner is GST registered"""
        for partner in self:
            partner.l10n_in_is_gst_registered = (
                partner.l10n_in_gst_treatment in ['regular', 'composition', 'special_economic_zone'] and
                bool(partner.l10n_in_gstin)
            )

    @api.constrains('l10n_in_gstin')
    def _check_gstin_format(self):
        """Validate GSTIN format"""
        for partner in self:
            if partner.l10n_in_gstin:
                # Basic format check
                if not re.match(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$',
                              partner.l10n_in_gstin):
                    raise ValidationError(_(
                        'Invalid GSTIN format for %(partner)s. '
                        'It should be in the format: 99AAAAA9999A9Z9',
                        partner=partner.name
                    ))

                # State code validation
                if partner.state_id and partner.state_id.l10n_in_tin:
                    if partner.l10n_in_gstin[:2] != partner.state_id.l10n_in_tin:
                        raise ValidationError(_(
                            'State code in GSTIN (%(gstin_state)s) does not match '
                            'partner\'s state code (%(partner_state)s) for %(partner)s',
                            gstin_state=partner.l10n_in_gstin[:2],
                            partner_state=partner.state_id.l10n_in_tin,
                            partner=partner.name
                        ))

    @api.constrains('l10n_in_pan')
    def _check_pan_format(self):
        """Validate PAN format"""
        for partner in self:
            if partner.l10n_in_pan:
                if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', partner.l10n_in_pan):
                    raise ValidationError(_(
                        'Invalid PAN format for %(partner)s. '
                        'It should be in the format: AAAAA9999A',
                        partner=partner.name
                    ))

    @api.onchange('l10n_in_gstin')
    def _onchange_l10n_in_gstin(self):
        """Auto-fill PAN based on GSTIN"""
        for partner in self:
            if partner.l10n_in_gstin and len(partner.l10n_in_gstin) >= 12:
                # PAN is characters 3-12 of GSTIN
                partner.l10n_in_pan = partner.l10n_in_gstin[2:12]

    @api.onchange('state_id', 'l10n_in_gst_treatment')
    def _onchange_state_id(self):
        """Handle state change implications for GST"""
        for partner in self:
            if partner.state_id and partner.state_id.country_id.code == 'IN':
                if partner.l10n_in_gst_treatment == 'overseas':
                    partner.l10n_in_gst_treatment = 'regular'
            elif partner.l10n_in_gst_treatment in ['regular', 'composition']:
                partner.l10n_in_gst_treatment = 'overseas'

    def _get_gst_treatment_display(self):
        """Get display name for GST treatment"""
        treatment_dict = dict(self._fields['l10n_in_gst_treatment'].selection)
        return treatment_dict.get(self.l10n_in_gst_treatment, '')

    def name_get(self):
        """Override to add GSTIN in partner name display"""
        result = super().name_get()
        if self.env.context.get('show_gstin'):
            result = [
                (record.id, f"{record.name} ({record.l10n_in_gstin})" if record.l10n_in_gstin else record.name)
                for record in self
            ]
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """Enable search by GSTIN"""
        args = args or []
        if name:
            args = ['|', ('name', operator, name), ('l10n_in_gstin', operator, name)] + args
        return super()._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)