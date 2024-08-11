from odoo import api, fields, models, _
from . import api_global_function


class Users(models.Model):
    _inherit = 'res.users'

    journal_id = fields.Many2one('account.journal', string="Payment Journal")

    def get_my_wallet(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        res_user_obj = self.env['res.users'].sudo().browse(args.get('userId'))
        try:
            account_move_line_list = []
            total_debit = 0.0
            total_credit = 0.0
            total_balance = 0.0
            if res_user_obj.journal_id and res_user_obj.journal_id.default_account_id:
                account_move_line_objs = self.env['account.move.line'].with_context(lang=lang).sudo().search(
                    [('account_id', '=', res_user_obj.journal_id.default_account_id.id),
                     ('parent_state', '=', 'posted')])
                for account_move_line_obj in account_move_line_objs:
                    total_debit += account_move_line_obj.debit
                    total_credit += account_move_line_obj.credit
                    total_balance += account_move_line_obj.balance
                    account_move_line_list.append({
                        'date': account_move_line_obj.date,
                        'move_name': account_move_line_obj.move_name,
                        'name': account_move_line_obj.name,
                        'amount_currency': account_move_line_obj.amount_currency,
                        'debit': account_move_line_obj.debit,
                        'credit': account_move_line_obj.credit,
                        'balance': account_move_line_obj.balance,
                        'ref': account_move_line_obj.ref,
                        'currency_id': account_move_line_obj.currency_id.id,
                        'currency_name': account_move_line_obj.currency_id.name,
                    })
        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        return {
            "Code": 200,
            "StatusDescription": "Success",
            "Data": {'total_debit': total_debit, 'total_credit': total_credit,
                     'total_balance': total_balance, 'transactions': account_move_line_list},
            "ArabicMessage": "تم إسترجاع حركات المندوب بنجاح",
            "EnglishMessage": "User account move have been Retrieved Successfully"
        }
