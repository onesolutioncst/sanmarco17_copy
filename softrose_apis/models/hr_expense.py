from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging
from . import api_global_function
from odoo.tests import Form

_logger = logging.getLogger(__name__)


class hr_expense(models.Model):
    _inherit = "hr.expense"

    def check_expense_vals(self, args):
        expense_vals = {}
        if args.get("expense_id", False):
            expense_vals.update({'id': args.get("expense_id", False)})
        try:
            user_id = args.get('userId') and int(args.get('userId'))
            res_user_obj = self.env['res.users'].sudo().browse(user_id)
            employee_obj = self.env['hr.employee'].sudo().search(
                [('user_id', '=', user_id), ('company_id', '=', res_user_obj.company_id.id)])
            if not employee_obj:
                return False, api_global_function.return_failed_request_vals("Employee Not found",
                                                                             "عفوا الموظف غير موجود")
            expense_vals.update({"employee_id": employee_obj[0].id})

            if not args.get('expense_name', False) and not args.get("expense_id", False):
                return False, api_global_function.return_failed_request_vals("Expense Name/Description Not provided",
                                                                             "عفوا اسم/وصف المصروفات مش موجود")
            expense_vals.update({'name': args.get('expense_name', False)})
            if not args.get('expense_categories_id', False):
                return False, api_global_function.return_failed_request_vals(
                    "Expense category is empty please check",
                    "عفوا امر المصروفات خالى من المنتجات ")
            if not self.env['product.product'].sudo().search(
                    [('id', '=', int(args.get('expense_categories_id', False)))]):
                return False, api_global_function.return_failed_request_vals("Expense Category ID Not Correct",
                                                                             "عفوا تصنيف المصروفات غير صحيح")
            expense_vals.update({'product_id': int(args.get('expense_categories_id', False))})
            if args.get('unit_amount', False) and args.get('unit_amount', False) <= 0.0:
                return False, api_global_function.return_failed_request_vals(
                    "Unit Amount must be greater than Zero",
                    "عفوا سعر الوحدة لابد ان تكون اكبر من الزيرو ")
            if args.get('total_amount', False) and args.get('total_amount', False) <= 0.0:
                return False, api_global_function.return_failed_request_vals(
                    "Total Amount must be greater than Zero",
                    "عفوا الاجمالى لابد ان تكون اكبر من الزيرو ")
            expense_vals.update({'unit_amount': args.get('expense_unit_price', 0.0)})
            if 'total_amount' not in args:
                expense_vals.update({'total_amount': args.get('unit_amount', False)*1})
            else:
                expense_vals.update({'total_amount': args.get('total_amount', False)})
            expense_vals.update({'date': args.get('expense_date', False)})
            expense_vals.update({'description': args.get('expense_description', False)})
            expense_vals.update({'payment_mode': args.get('company_account', False)})
        except Exception as e:
            arabic_message = "%s  " % _(str(e)),
            englishmessage = "%s." % _(str(e))
            return False, api_global_function.return_failed_request_vals(englishmessage, arabic_message)
        return True, expense_vals

    @api.model
    def add_new_expense(self, **args):
        request_id = args.get("expense_id", False)
        check_vals, expense_vals = self.check_expense_vals(args)
        if not check_vals:
            return expense_vals
        try:
            if not request_id:
                hr_expense_obj = self.with_user(args.get('userId')).sudo().create(expense_vals)
            else:
                # Update Request ID
                hr_expense_obj = self.with_user(args.get('userId')).sudo().browse(request_id)
                hr_expense_obj.with_user(args.get('userId')).sudo().write(expense_vals)
            hr_expense_obj.unit_amount = args.get('expense_unit_price', 0.0)
            hr_expense_obj.total_amount = args.get('expense_unit_price', 0.0)
            hr_expense_obj.payment_mode = 'company_account'
        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        request_dic = {
            "expense_id": hr_expense_obj.id,
            "expense_name": hr_expense_obj.name,
            "expense_categories_id": hr_expense_obj.product_id.id,
            "expense_categories_name": hr_expense_obj.product_id.name,
            "expense_unit_price": hr_expense_obj.unit_amount,
            "expense_description": hr_expense_obj.description or "",
            "expense_date": hr_expense_obj.date,
            "expense_state": dict(hr_expense_obj._fields['state'].selection).get(hr_expense_obj.state)
        }
        if not request_id:
            return {
                "Code": 200,
                "StatusDescription": "Success",
                "Data": request_dic,
                "ArabicMessage": "تم انشاء الطلب بنجاح رقم(%s)  " % str(hr_expense_obj.id),
                "EnglishMessage": "Request Number (%s)has been created successfully." % str(hr_expense_obj.id)
            }
        else:
            return {
                "Code": 200,
                "StatusDescription": "Success",
                "Data": request_dic,
                "ArabicMessage": "تم تعديل الطلب بنجاح رقم(%s)  " % str(hr_expense_obj.id),
                "EnglishMessage": "Request Number (%s)has been updated successfully." % str(hr_expense_obj.id)
            }

    @api.model
    def delete_my_expense(self, **args):
        try:
            if not args.get('expense_id', False):
                return False, api_global_function.return_failed_request_vals(
                    "Expense ID is empty please check",
                    "عفوا امر المصروفات غير موجود ")
            request_id = args.get("expense_id", False)
            hr_expense_obj = self.with_user(args.get('userId')).sudo().browse(request_id)
            if hr_expense_obj.state != 'draft':
                return False, api_global_function.return_failed_request_vals(
                    "Expense Status Not in draft mode so you cant delete it",
                    "عفوا لا يمكن حذف الطلب حيث انه ليس فى وضع المسودة")
            hr_expense_obj.with_user(args.get('userId')).sudo().unlink()
        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        return api_global_function.return_success_delete_api(request_id)

    def do_action_in_my_expense(self, **args):
        try:
            user_obj = self.env['res.users'].browse(args.get('userId'))
            if not args.get('expense_id', False):
                return False, api_global_function.return_failed_request_vals(
                    "Expense ID is empty please check",
                    "عفوا امر المصروفات غير موجود ")
            request_id = args.get("expense_id", False)
            hr_expense_obj = self.with_user(args.get('userId')).sudo().browse(request_id)
            if hr_expense_obj.state != 'draft':
                return False, api_global_function.return_failed_request_vals(
                    "Expense Status Not in draft mode so you cant delete it",
                    "عفوا لا يمكن حذف الطلب حيث انه ليس فى وضع المسودة")
            if args.get('expense_action', False) and args.get('expense_action', False) not in ['submit', 'submit_to_manager','approve']:
                return False, api_global_function.return_failed_request_vals(
                    "Expense action is not correct",
                    "عفوا اكشن المصروفات غير صحيح ")
            if args.get('expense_action', False) == 'submit':
                hr_expense_action = hr_expense_obj.with_user(args.get('userId')).with_company(user_obj.company_id.id).sudo().action_submit_expenses()
                expense_wizard = Form(
                    self.env['hr.expense.sheet'].with_user(args.get('userId')).with_company(user_obj.company_id.id).sudo().with_context(hr_expense_action['context'])).save()
            if args.get('expense_action', False) == 'submit_to_manager':
                if hr_expense_obj.sheet_id:
                    hr_expense_obj.with_user(args.get('userId')).sudo().sheet_id.action_submit_sheet()
            if args.get('expense_action', False) == 'approve':
                if hr_expense_obj.sheet_id:
                    hr_expense_obj.with_user(args.get('userId')).sudo().sheet_id.approve_expense_sheets()


        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        return api_global_function.return_success_update_api(hr_expense_obj.id, hr_expense_obj.id)

    def get_all_my_expenses(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_id = args.get('userId') and int(args.get('userId'))
        domain = []
        hr_employee_objs = self.env['hr.employee'].with_context(lang=lang).sudo().search([('user_id', '=', user_id)])
        if hr_employee_objs:
            domain.append(('employee_id', 'in', hr_employee_objs.ids))
        if args.get('expense_id', False):
            if not self.env['hr.expense'].with_context(lang=lang).sudo().search(
                    [('id', '=', int(args.get('expense_id', False)))]):
                return False, api_global_function.return_failed_request_vals("The Expense not exist profile",
                                                                             "عفوا امر المصروف غير موجود")
            domain.append(('id', '=', int(args.get('expense_id', False))))
        hr_expense_objs = self.with_context(lang=lang).sudo().search(domain, order="id desc")
        hr_expense_dic = []
        for hr_expense_obj in hr_expense_objs:
            hr_expense_dic.append(
                {
                    "expense_id": hr_expense_obj.id,
                    "expense_name": hr_expense_obj.name,
                    "expense_categories_id": hr_expense_obj.product_id.id,
                    "expense_categories_name": hr_expense_obj.product_id.name,
                    "expense_unit_price": hr_expense_obj.unit_amount,
                    "expense_description": hr_expense_obj.description or "",
                    "expense_date": hr_expense_obj.date,
                    "expense_state": dict(hr_expense_obj._fields['state'].selection).get(hr_expense_obj.state)
                }
            )
        return api_global_function.return_success_list_api(hr_expense_dic)

    def add_attachment_to_my_expense(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_id = args.get('userId') and int(args.get('userId'))
        hr_employee_objs = self.env['hr.employee'].with_context(lang=lang).sudo().search([('user_id', '=', user_id)])
        domain = []
        # if hr_employee_objs:
        #     domain.append(('employee_id','in',hr_employee_objs.ids))
        if not args.get('attachment', False):
            return False, api_global_function.return_failed_request_vals("The Expense Attachment is not provided",
                                                                         "عفوا المرفق الخاص بالمصروف غير موجود")
        if not args.get('attachment_name', False):
            return False, api_global_function.return_failed_request_vals("The Expense Attachment Name is not provided",
                                                                         "عفوا اسم المرفق الخاص بالمصروف غير موجود")
        if not args.get('expense_id', False):
            return False, api_global_function.return_failed_request_vals("The Expense not provided",
                                                                         "عفوا امر المصروف غير موجود")
        if not self.env['hr.expense'].with_context(lang=lang).sudo().search(
                [('id', '=', int(args.get('expense_id', False)))]):
            return False, api_global_function.return_failed_request_vals("The Expense not exist profile",
                                                                         "عفوا امر المصروف غير صحيح")
        hr_expense_obj = self.with_context(lang=lang).sudo().browse(int(args.get('expense_id', False)))
        # 1 - create attachment
        attachment_obj = self.env['ir.attachment'].with_user(user_id).sudo().create({
            'name': args.get('attachment_name', ''),
            'type': 'binary',
            'datas': args.get('attachment', ''),
            # 'mimetype':args.get('attachment_type', False),
            'res_model': 'hr.expense',
            'res_id':int(args.get('expense_id', False)),
            'res_name': hr_expense_obj.name,
        })
        hr_expense_obj.attach_document()
        return api_global_function.return_success_update_api(hr_expense_obj.id, hr_expense_obj.id)

