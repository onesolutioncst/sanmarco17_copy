# -*- coding : utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)
from odoo.tools import SQL
class SaleOrderUpdate(models.Model):
    _inherit = 'sale.order'

    invoiced_amount = fields.Float(string = 'Invoiced Amount' ,compute ='_compute_invoice_amount',compute_sudo=True , readonly=False , store=True)
    amount_due = fields.Float(string ='Amount Due',compute ='_compute_invoice_amount',compute_sudo=True, readonly=False, store=True)
    paid_amount = fields.Float(string ='Paid Amount',compute ='_compute_invoice_amount',compute_sudo=True ,default=0.0, readonly=False, store=True)
    remaining_amount = fields.Float(string='Remaining Amount', compute='_compute_invoice_amount', compute_sudo=True, default=0.0,
                               readonly=False, store=True)
    amount_paid_percent = fields.Float(compute = 'action_amount_paid',compute_sudo=True, readonly=False)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id)
    recalc_fields = fields.Boolean(compute="_compute_invoice_amount")

    @api.onchange('invoice_count', 'invoice_ids', 'invoice_status')
    @api.depends('invoice_count', 'invoice_ids', 'invoice_status')
    def _compute_invoice_amount(self):
        for record in self:
            invoice_id = self.env['account.move'].search([('invoice_origin','=', record.name),
                                                          ('state','in',['draft','posted']),
                                                          ('payment_state', 'not in', ['reversed', 'invoicing_legacy'])])
            amount_total = 0.0
            amount_residual = 0.0
            record.recalc_fields = True
            for invoice in self.invoice_ids:
                amount_total += invoice.amount_total
                amount_residual += invoice.amount_residual
            record.invoiced_amount = amount_total
            record.amount_due = amount_residual
            record.paid_amount = amount_total - amount_residual
            record.remaining_amount = record.amount_total - amount_total

    @api.depends('paid_amount', 'invoiced_amount')
    def action_amount_paid(self):
        for record in self:
            try:
                if record.invoiced_amount:
                    record.amount_paid_percent = round(100 * record.paid_amount / record.invoiced_amount, 3)
                else:
                    record.amount_paid_percent = 0.0
            except Exception as e:
                _logger.error(f"Error in action_amount_paid: {e}")
                record.amount_paid_percent = 0.0