from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

from odoo.exceptions import ValidationError
from . import api_global_function

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.model
    def get_all_payment_order(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_obj = self.env['res.users'].browse(args.get('userId'))
        try:
            if args.get("sales_order_id", False):
                sale_order_obj = self.env['sale.order'].sudo().search(
                    [('id', '=', int(args.get("sales_order_id", False)))])
                if not sale_order_obj:
                    return {
                        "Code": 500,
                        "StatusDescription": "Failed",
                        "Data": {},
                        "ArabicMessage": "رقم امر البيع غير صحيح",
                        "EnglishMessage": "Sale order ID is not correct"
                    }
            else:
                return {
                    "Code": 500,
                    "StatusDescription": "Failed",
                    "Data": {},
                    "ArabicMessage": "رقم امر البيع غير موجود",
                    "EnglishMessage": "Sale order ID is not Provided"
                }
        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        invoices = sale_order_obj.order_line.invoice_lines.move_id.filtered(
            lambda r: r.move_type in ('out_invoice', 'out_refund'))
        invoices_list = []
        for invoice_obj in invoices:
            payments_widget_value = invoice_obj.invoice_payments_widget
            print("account_payment_objs", payments_widget_value)
            invoice_obj_dic = {
                "invoice_id": invoice_obj.id,
                "invoice_name": invoice_obj.name,
                "invoice_status": dict(invoice_obj._fields['state'].selection).get(invoice_obj.state),
                "invoice_date": invoice_obj.invoice_date,
                "invoice_payment_state": dict(invoice_obj._fields['payment_state'].selection).get(
                    invoice_obj.payment_state),
                "invoice_amount_total": invoice_obj.amount_total,
                "invoice_amount_paid": invoice_obj.amount_total - invoice_obj.amount_residual,
                "invoice_amount_residual": invoice_obj.amount_residual,
            }
            if payments_widget_value:
                invoice_obj_dic.update({'invoice_payment': payments_widget_value.get('content')})
            invoices_list.append(invoice_obj_dic)
        sale_order_dic = {
            "sales_order_id ": sale_order_obj.id,
            "sales_order_name": sale_order_obj.name,
            "sales_order_date": sale_order_obj.date_order,
            "sales_order_order_type": sale_order_obj.order_type,
            "sales_order_amount": sale_order_obj.amount_untaxed,
            "sales_order_tax_amount": sale_order_obj.amount_tax,
            "sales_order_total_amount": sale_order_obj.amount_total,
            "sales_order_notes": sale_order_obj.note or '',
            'invoice_list': invoices_list,
        }
        return {
            "Code": 200,
            "StatusDescription": "Success",
            "Data": sale_order_dic,
            "ArabicMessage": "تم إسترجاع مدفوعات طلب العميل بنجاح",
            "EnglishMessage": "Customer Payment Orders have been Retrieved Successfully"
        }

    @api.model
    def add_new_payment_order(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_obj = self.env['res.users'].browse(args.get('userId'))
        domain = []
        try:
            if args.get("sales_order_id", False):
                sale_order_obj = self.env['sale.order'].sudo().search(
                    [('id', '=', int(args.get("sales_order_id", False)))])
                if not sale_order_obj:
                    return {
                        "Code": 500,
                        "StatusDescription": "Failed",
                        "Data": {},
                        "ArabicMessage": "رقم امر البيع غير صحيح",
                        "EnglishMessage": "Sale order ID is not correct"
                    }
                # domain.append(('sale_id', '=', args.get("sales_order_id", False)))
            else:
                return {
                    "Code": 500,
                    "StatusDescription": "Failed",
                    "Data": {},
                    "ArabicMessage": "رقم امر البيع غير موجود",
                    "EnglishMessage": "Sale order ID is not Provided"
                }
            if args.get("invoice_id", False):
                account_move_obj = self.env['account.move'].sudo().search(
                    [('id', '=', int(args.get("invoice_id", False)))])
                if not account_move_obj:
                    return {
                        "Code": 500,
                        "StatusDescription": "Failed",
                        "Data": {},
                        "ArabicMessage": "رقم الفاتورة غير صحيح",
                        "EnglishMessage": "Invoice ID is not Correct"
                    }
            else:
                return {
                    "Code": 500,
                    "StatusDescription": "Failed",
                    "Data": {},
                    "ArabicMessage": "رقم الفاتورة غير موجود",
                    "EnglishMessage": "Invoice ID is not Provided"
                }
            if not args.get("payment_amount", False):
                return {
                    "Code": 500,
                    "StatusDescription": "Failed",
                    "Data": {},
                    "ArabicMessage": "القيمه المدفوعه غير موجودة ",
                    "EnglishMessage": "Payment amount is not Provided"
                }
            if float(args.get("payment_amount", False)) <= 0.0:
                return {
                    "Code": 500,
                    "StatusDescription": "Failed",
                    "Data": {},
                    "ArabicMessage": "القيمه المدفوعه يجب ان تكون اكبر من الصفر ",
                    "EnglishMessage": "Payment amount must be greater than Zero"
                }
        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))

        journal_id = account_move_obj.invoice_user_id.journal_id
        if not journal_id:
            return {
                "Code": 500,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "المحفظه الخاصه بالمندوب غير موجودة يرجى مراجعه الحسابات",
                "EnglishMessage": "Payment Journal on Salesperson is not found please ack accounting"
            }
        try:
            if args.get('payment_amount', False) > account_move_obj.amount_residual:
                return {
                    "Code": 500,
                    "StatusDescription": "Failed",
                    "Data": {},
                    "ArabicMessage": "عفوا المبلغ المدفوع اكبر من المتبقى على الفاتورة يرجى المراجعة ",
                    "EnglishMessage": "Sorry, Payment amount is greater than invoice residual amount, please check"
                }
            account_payment_obj = self.env['account.payment.register'].with_user(user_obj.id).with_company(
                user_obj.company_id.id).sudo().with_context(active_ids=[args.get('invoice_id', False)],
                                                            active_model='account.move').sudo().create(
                {'journal_id': journal_id.id, "amount": args.get('payment_amount', False)})._create_payments()
        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        # account_payment_obj = self.env['stock.picking'].browse(account_register_payment_action['res_id'])
        account_payment_list = []
        for invoice_obj in account_payment_obj.reconciled_invoice_ids:
            sale_order_objs = invoice_obj.line_ids.sale_line_ids.order_id
            invoice_order_obj = {
                "invoice_id": invoice_obj.id,
                "invoice_name": invoice_obj.name,
                "invoice_status": dict(invoice_obj._fields['state'].selection).get(invoice_obj.state),
                "invoice_date": invoice_obj.invoice_date,
                "invoice_payment_state": dict(invoice_obj._fields['payment_state'].selection).get(
                    invoice_obj.payment_state),
                "invoice_amount_total": invoice_obj.amount_total,
                "invoice_amount_paid": invoice_obj.amount_total - invoice_obj.amount_residual,
                "invoice_amount_residual": invoice_obj.amount_residual,
                # "invoice_payment": invoice_obj.invoice_payments_widget.get('content'),
                # 'sale_order_list': sale_order_list
            }
            for sale_order_obj in sale_order_objs:
                sale_order_obj = {
                    "sales_order_id ": sale_order_obj.id,
                    "sales_order_name": sale_order_obj.name,
                    "sales_order_date": sale_order_obj.date_order,
                    "sales_order_order_type": sale_order_obj.order_type,
                    # "sales_order_amount": sale_order_obj.tax_totals,
                    "sales_order_amount": sale_order_obj.amount_untaxed,
                    # "sales_order_tax_name": "VAT 14 %",
                    "sales_order_tax_amount": sale_order_obj.amount_tax,
                    "sales_order_total_amount": sale_order_obj.amount_total,
                    "sales_order_notes": sale_order_obj.note or '',
                    # 'sale_order_line': order_line_list,
                }
        account_payment_list.append(
            {
                'payment_id': account_payment_obj.id,
                "name": account_payment_obj.name,
                "journal_name": account_payment_obj.journal_id.name,
                "amount": account_payment_obj.amount,
                "currency_id": account_payment_obj.currency_id.id,
                "date": account_payment_obj.date,
                # "partial_id": 10,
                # "account_payment_id": 10,
                "payment_method_name": account_payment_obj.payment_method_line_id.name,
                "move_id": account_payment_obj.move_id.id,
                "ref": account_payment_obj.ref,
                # "is_exchange": false,
                # "amount_company_currency": "90.000  د.ك ",
                # "amount_foreign_currency": false
                # 'invoice_list': invoice_list
            }
        )
        invoice_order_obj.update(
            {
                'invoice_payment': account_payment_list
            }
        )
        sale_order_obj.update(
            {
                'invoice_list': invoice_order_obj,
            }
        )
        return {
            "Code": 200,
            "StatusDescription": "Success",
            "Data": sale_order_obj,
            "ArabicMessage": "تم اضافة  دفع لطلب العميل بنجاح",
            "EnglishMessage": "Customer Payment Orders has been Added Successfully"
        }
