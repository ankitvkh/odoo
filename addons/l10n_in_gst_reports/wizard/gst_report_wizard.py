from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class GSTReportWizard(models.TransientModel):
    _name = 'gst.report.wizard'
    _description = 'GST Report Generation Wizard'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    report_type = fields.Selection([
        ('gstr1', 'GSTR-1'),
        ('gstr3b', 'GSTR-3B')
    ], string='Report Type', required=True, default='gstr1')

    period_type = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly')
    ], string='Period Type', required=True, default='monthly')

    month = fields.Selection([
        ('01', 'January'),
        ('02', 'February'),
        ('03', 'March'),
        ('04', 'April'),
        ('05', 'May'),
        ('06', 'June'),
        ('07', 'July'),
        ('08', 'August'),
        ('09', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December')
    ], string='Month')

    quarter = fields.Selection([
        ('1', 'Q1 - April to June'),
        ('2', 'Q2 - July to September'),
        ('3', 'Q3 - October to December'),
        ('4', 'Q4 - January to March')
    ], string='Quarter')

    financial_year = fields.Selection(
        selection='_get_financial_years',
        string='Financial Year',
        required=True,
        default=lambda self: self._get_default_financial_year()
    )

    @api.model
    def _get_financial_years(self):
        current_year = datetime.now().year
        years = []
        # Generate financial years list (current year - 2 to current year + 1)
        for year in range(current_year - 2, current_year + 2):
            years.append((str(year), f'{year}-{year + 1}'))
        return years

    @api.model
    def _get_default_financial_year(self):
        today = fields.Date.today()
        if today.month < 4:  # Before April
            return str(today.year - 1)
        return str(today.year)

    @api.onchange('period_type')
    def _onchange_period_type(self):
        self.month = False
        self.quarter = False

        # Set default based on current date
        today = fields.Date.today()
        if self.period_type == 'monthly':
            self.month = str(today.month).zfill(2)
        else:
            quarter = ((today.month - 1) // 3) + 1
            self.quarter = str(quarter)

    def action_generate_report(self):
        self.ensure_one()

        # Validate selections
        if self.period_type == 'monthly' and not self.month:
            raise UserError(_('Please select a month.'))
        if self.period_type == 'quarterly' and not self.quarter:
            raise UserError(_('Please select a quarter.'))

        # Calculate date range
        date_from, date_to = self._get_date_range()

        # Check for existing report
        existing_report = self.env['gst.report'].search([
            ('company_id', '=', self.company_id.id),
            ('report_type', '=', self.report_type),
            ('date_from', '=', date_from),
            ('date_to', '=', date_to),
            ('state', '!=', 'cancelled')
        ])

        if existing_report:
            raise UserError(_(
                'A report already exists for this period. Please cancel it first if you want to regenerate.'
            ))

        # Create new report
        report = self.env['gst.report'].create({
            'company_id': self.company_id.id,
            'report_type': self.report_type,
            'date_from': date_from,
            'date_to': date_to,
        })

        # Generate report data
        report.action_generate_report()

        # Return action to view the report
        return {
            'name': _('GST Report'),
            'type': 'ir.actions.act_window',
            'res_model': 'gst.report',
            'res_id': report.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _get_date_range(self):
        """Calculate start and end dates based on period selection"""
        year = int(self.financial_year)

        if self.period_type == 'monthly':
            month = int(self.month)
            # For months after March, use the selected year
            # For months January to March, use the next year
            if month <= 3:
                year += 1

            date_from = fields.Date.from_string(f'{year}-{month:02d}-01')
            date_to = date_from + relativedelta(months=1, days=-1)

        else:  # quarterly
            quarter = int(self.quarter)
            # First month of the quarter (1->4, 2->7, 3->10, 4->1)
            month = 3 * quarter + 1 if quarter != 4 else 1
            # For Q4 (Jan-Mar), use the next year
            if quarter == 4:
                year += 1

            date_from = fields.Date.from_string(f'{year}-{month:02d}-01')
            date_to = date_from + relativedelta(months=3, days=-1)

        return date_from, date_to