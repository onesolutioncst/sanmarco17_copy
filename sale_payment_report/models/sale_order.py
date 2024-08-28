from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging
from datetime import datetime, timedelta
_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class sale_order(models.Model):
    _inherit = "sale.order"


    def get_sales_payment(self):
        for record in self:
            balance = record.amount_total
            account_payment_list = []
            sale_payment_list = [{
                'date_order': record.date_order.date(),
                'name' : record.name,
                'client_order_ref': record.client_order_ref or '',
                'debit': record.amount_total,
                'credit': 0.0,
                'balance': record.amount_total,
            }]
            payment_list = []
            for invoice_obj in record.invoice_ids:
                payments = self.env['account.payment'].search([('move_id', '=', invoice_obj.id)],
                                                              order='id asc')  # Order payments by their ID
                if invoice_obj.invoice_payments_widget and 'content' in invoice_obj.invoice_payments_widget:
                    for invoice_payments_widget in invoice_obj.invoice_payments_widget['content']:
                        payment_list.append(invoice_payments_widget['account_payment_id'])
            for payment_obj in self.env['account.payment'].search([('id', 'in', payment_list)], order='id desc'):
                sale_payment_list.append(
                    {
                        'date_order': payment_obj.date,
                        'name': payment_obj.name,
                        'client_order_ref': payment_obj.ref,
                        'debit': 0.0,
                        'credit': payment_obj.amount,
                        'balance': round(balance - payment_obj.amount,2),
                    }
                )
                balance = round(balance - payment_obj.amount,2)

            # for invoice_obj in record.invoice_ids:
            #     payments = self.env['account.payment'].search([('move_id', '=', invoice_obj.id)], order='id asc')  # Order payments by their ID
            #     if invoice_obj.invoice_payments_widget and 'content' in invoice_obj.invoice_payments_widget:
            #         for invoice_payments_widget in invoice_obj.invoice_payments_widget['content']:
            #             account_payment_list.append(invoice_payments_widget['account_payment_id'])
            #             sale_payment_list.append(
            #                 {
            #                     'date_order': invoice_payments_widget['date'],
            #                     'name': invoice_payments_widget['name'],
            #                     'client_order_ref': invoice_payments_widget['ref'],
            #                     'debit': 0.0,
            #                     'credit': invoice_payments_widget['amount'],
            #                     'balance': balance - invoice_payments_widget['amount'],
            #                 }
            #             )
            #             balance = balance - invoice_payments_widget['amount']
            return sale_payment_list

