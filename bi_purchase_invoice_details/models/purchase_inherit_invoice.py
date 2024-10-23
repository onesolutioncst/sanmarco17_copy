# -*- coding : utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class PurchaseOrderUpdate(models.Model):
	_inherit = 'purchase.order'

	invoiced_amount = fields.Float(string = 'Invoiced Amount',compute ='_compute_invoiced_amount',compute_sudo=True, store=True)
	amount_due = fields.Float(string ='Amount Due', compute ='_compute_invoiced_amount',compute_sudo=True, store=True)
	paid_amount = fields.Float(string ='Paid Amount', compute ='_compute_invoiced_amount',compute_sudo=True, store=True)
	remaining_amount = fields.Float(string='Remaining Amount', compute='_compute_invoiced_amount', compute_sudo=True,store=True)
	recalc_fields = fields.Boolean(compute="_compute_invoiced_amount")
	amount_paid_percent = fields.Float(compute = 'action_amount_paid',compute_sudo=True)
	currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id)

	@api.depends('paid_amount','invoiced_amount', 'amount_due')
	def _compute_invoiced_amount(self):
		for record in self:
			record.recalc_fields = True
			invoiced_amount = 0.0
			amount_due = 0.0
			for bill in self.invoice_ids.filtered(lambda invoice: invoice.state in ['draft', 'posted']):
				invoiced_amount += bill.amount_total
				amount_due += bill.amount_residual
			record.invoiced_amount = invoiced_amount
			record.amount_due = amount_due
			record.paid_amount = invoiced_amount - amount_due
			record.remaining_amount = record.amount_total - invoiced_amount


	
	@api.depends('paid_amount','invoiced_amount', 'amount_due')
	def _computedue(self):
		for record in self:
			invoice_ids = self.env['account.move'].search(['&',('invoice_origin','=', record.name),'|',('state','=','draft'),('state','=','posted'),('payment_state', 'not in', ['reversed', 'invoicing_legacy'])])
			amount = 0
			if invoice_ids:
				for inv in invoice_ids:
					amount  += inv.amount_residual   
					record.amount_due = amount
			else:
				record.amount_due = amount
			

	@api.onchange('invoiced_amount','amount_due')
	def _computepaid(self):
		self.paid_amount = float(self.invoiced_amount) - float(self.amount_due)		


	@api.depends('paid_amount','invoiced_amount')
	def action_amount_paid(self):
		if self.invoiced_amount :
			self.amount_paid_percent = round(100 * self.paid_amount / self.invoiced_amount, 3)
		return self.amount_paid_percent
