from odoo import api, fields, models
from datetime import date, timedelta


class PurchaseDashboard(models.TransientModel):
    _name = 'material.indent.purchase.dashboard'
    _description = 'Purchase Dashboard Statistics'

    # ---------- Material Indent KPIs ----------
    indent_draft_count = fields.Integer(
        string='Draft Indents', compute='_compute_indent_stats')
    indent_submitted_count = fields.Integer(
        string='Pending Approval', compute='_compute_indent_stats')
    indent_approved_count = fields.Integer(
        string='Approved Indents', compute='_compute_indent_stats')
    indent_cancel_count = fields.Integer(
        string='Cancelled Indents', compute='_compute_indent_stats')

    # ---------- Purchase Order KPIs ----------
    rfq_count = fields.Integer(
        string='RFQs', compute='_compute_po_stats')
    po_count = fields.Integer(
        string='Purchase Orders', compute='_compute_po_stats')
    po_to_approve_count = fields.Integer(
        string='To Approve', compute='_compute_po_stats')
    total_spend_this_month = fields.Float(
        string='Spend This Month', compute='_compute_po_stats')
    total_spend_all = fields.Float(
        string='Total Spend (All)', compute='_compute_po_stats')
    waiting_bills_count = fields.Integer(
        string='Waiting Bills', compute='_compute_po_stats')

    @api.depends()
    def _compute_indent_stats(self):
        Indent = self.env['material.indent']
        for rec in self:
            rec.indent_draft_count = Indent.search_count([('state', '=', 'draft')])
            rec.indent_submitted_count = Indent.search_count([('state', '=', 'submitted')])
            rec.indent_approved_count = Indent.search_count([('state', '=', 'approved')])
            rec.indent_cancel_count = Indent.search_count([('state', '=', 'cancel')])

    @api.depends()
    def _compute_po_stats(self):
        PO = self.env['purchase.order']
        today = date.today()
        month_start = today.replace(day=1)

        for rec in self:
            rec.rfq_count = PO.search_count([
                ('state', 'in', ('draft', 'sent'))
            ])
            rec.po_count = PO.search_count([
                ('state', 'in', ('purchase', 'done'))
            ])
            rec.po_to_approve_count = PO.search_count([
                ('state', '=', 'to approve')
            ])
            rec.waiting_bills_count = PO.search_count([
                ('state', 'in', ('purchase', 'done')),
                ('invoice_status', '=', 'to invoice'),
            ])

            # Spend this calendar month
            month_orders = PO.search([
                ('state', 'in', ('purchase', 'done')),
                ('date_approve', '>=', fields.Datetime.to_datetime(month_start)),
            ])
            rec.total_spend_this_month = sum(month_orders.mapped('amount_total'))

            # All-time spend
            all_orders = PO.search([('state', 'in', ('purchase', 'done'))])
            rec.total_spend_all = sum(all_orders.mapped('amount_total'))

    # ---------- Navigation actions ----------

    def action_view_draft_indents(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Draft Indents',
            'res_model': 'material.indent',
            'view_mode': 'list,form',
            'domain': [('state', '=', 'draft')],
        }

    def action_view_submitted_indents(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Indents Pending Approval',
            'res_model': 'material.indent',
            'view_mode': 'list,form',
            'domain': [('state', '=', 'submitted')],
        }

    def action_view_approved_indents(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Approved Indents',
            'res_model': 'material.indent',
            'view_mode': 'list,form',
            'domain': [('state', '=', 'approved')],
        }

    def action_view_rfqs(self):
        return self.env.ref('purchase.purchase_rfq').read()[0]

    def action_view_purchase_orders(self):
        return self.env.ref('purchase.purchase_form_action').read()[0]

    def action_view_to_approve(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Orders to Approve',
            'res_model': 'purchase.order',
            'view_mode': 'list,form',
            'domain': [('state', '=', 'to approve')],
        }

    def action_view_waiting_bills(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Waiting Bills',
            'res_model': 'purchase.order',
            'view_mode': 'list,form',
            'domain': [
                ('state', 'in', ('purchase', 'done')),
                ('invoice_status', '=', 'to invoice'),
            ],
        }
