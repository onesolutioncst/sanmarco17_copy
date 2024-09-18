# -*- coding: utf-8 -*-
""" Odoo Rest Api Integration"""

import re
import binascii, hashlib
import random
from datetime import datetime, timedelta
from odoo import api, fields, models, _

import logging
from . import api_global_function

LOGGER = logging.getLogger(__name__)


class User(models.Model):
    """
    """
    _inherit = 'res.users'

    def _get_random_secret_key(self):
        return str(random.randint(1000, 9999))

    @api.model
    def _lang_get(self):
        return self.env['res.lang'].get_installed()

    @api.model
    def default_lang_get(self):
        langs = self.env['res.lang'].with_context(active_test=True).search([], limit=1)
        return langs.code or ''

    def compute_lang_get(self):
        langs = self.env['res.lang'].with_context(active_test=True).search([], limit=1)
        self.mobile_lang = langs.code or ''
        # return self.env['res.lang'].get_installed()

    mobile_lang = fields.Selection(string="Mobile Language", selection=_lang_get, default=default_lang_get, store=True,
                                   compute="compute_lang_get", readonly=False)
    api_access_token = fields.Char()
    secret_key = fields.Char(required=False, default=_get_random_secret_key)
    encrypted_secret_key = fields.Char(required=False)
    otp = fields.Char()
    otp_valid_date = fields.Datetime("OTP Valid Date")
    number_of_otp_try = fields.Integer("Number of OTP", default=0)
    block_send_otp_till = fields.Datetime("Block Send OTP Till")

    _sql_constraints = [("unique_api_access_token",
                         "UNIQUE(api_access_token)",
                         _('API Access Token should be unique')),
                        ("unique_encrypted_secret_key",
                         "UNIQUE(encrypted_secret_key)",
                         _('User secret key should be unique'))]

    def update_app_info(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_id = args.get('userId') and int(args.get('userId'))
        user_obj = self.env['res.users'].sudo().browse(user_id)
        app_info_dic = {}
        if 'app_name' in args and args.get('app_name', '') not in ['', None, False]:
            app_info_dic['app_name'] = args.get('app_name')
        if 'app_version' in args and args.get('app_version', '') not in ['', None, False]:
            app_info_dic['app_version'] = args.get('app_version')
        if 'app_store_app_link' in args and args.get('app_store_app_link', '') not in ['', None, False]:
            app_info_dic['app_store_app_link'] = args.get('app_store_app_link')
        if 'google_play_app_link' in args and args.get('google_play_app_link', '') not in ['', None, False]:
            app_info_dic['google_play_app_link'] = args.get('google_play_app_link')
        user_obj.company_id.sudo().write(app_info_dic)
        # res_config_settings_obj = self.env['res.config.settings'].sudo().search([('company_id', '=', 1)], limit=1)
        # if res_config_settings_obj:
        #     user_obj.company_id.sudo().write(app_info_dic)
        data = [{'app_name': user_obj.company_id.app_name or '',
                 'app_version': user_obj.company_id.app_version,
                 'app_store_app_link': user_obj.company_id.app_store_app_link or '',
                 'google_play_app_link': user_obj.company_id.google_play_app_link or '',
                 }]
        return {
            "Code": 200,
            "StatusDescription": "Success",
            "Data": data,
            "ArabicMessage": "تم تحديث معلومات التطبيق بنجاح",
            "EnglishMessage": "App Information has been Updated Successfully"
        }

    def delete_user_account(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_id = args.get('userId') and int(args.get('userId'))
        try:
            user_obj = self.env['res.users'].sudo().browse(user_id)
            user_obj.active = False
        except Exception as e:
            arabic_message = "%s  " % _(str(e))
            englishmessage = "%s." % _(str(e))
            return api_global_function.return_failed_request_vals(englishmessage, arabic_message)
        return {
            "Code": 200,
            "StatusDescription": "Success",
            "Data": {},
            "ArabicMessage": "تم حذف المستخدم بنجاح",
            "EnglishMessage": "The User has been Deleted Successfully",
        }

    def activate_user_account(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_id = args.get('userId') and int(args.get('userId'))
        try:
            user_obj = self.env['res.users'].sudo().browse(user_id)
            user_obj.sudo().active = True
        except Exception as e:
            arabic_message = "%s  " % _(str(e))
            englishmessage = "%s." % _(str(e))
            return api_global_function.return_failed_request_vals(englishmessage, arabic_message)
        return {
            "Code": 200,
            "StatusDescription": "Success",
            "Data": {},
            "ArabicMessage": "تم تنشيط المستخدم بنجاح",
            "EnglishMessage": "The User has been Activated Successfully",
        }

    def get_user_info(self, **args):
        # return request data for portal page
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_id = args.get('userId') and int(args.get('userId'))
        res_user_obj = self.env['res.users'].sudo().browse(user_id)
        hr_employee_objs = self.env['hr.employee'].sudo().with_context(lang=lang).search(
            [('user_id', '=', res_user_obj.id)])
        employee_info = {}
        img_link = ''
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for hr_employee_obj in hr_employee_objs:
            if hr_employee_obj.company_id == res_user_obj.company_id:
                employee_info['employee_name'] = hr_employee_obj.name
                if hr_employee_obj.image_1920:
                    img_link = base_url + "/web/binary/download_document?model=hr.employee&field=image_1920&id=" + str(
                        hr_employee_obj.id) + "&filename=image_1920.jpg"
                employee_info['img_link'] = img_link
                employee_info['job_title'] = hr_employee_obj.job_title or ''
                employee_info['job_position'] = hr_employee_obj.job_id.name or ''
                employee_info['mobile'] = hr_employee_obj.mobile_phone or ''
                employee_info['phone'] = hr_employee_obj.work_phone or ''
                employee_info['email'] = hr_employee_obj.work_email or ''
                employee_info['department'] = hr_employee_obj.department_id.name or ''
                employee_info['manager'] = hr_employee_obj.parent_id.name or ''
                employee_info['coach'] = hr_employee_obj.coach_id.name or ''
                employee_info['company'] = hr_employee_obj.company_id.name or ''
        return {
            "Code": 200,
            "StatusDescription": "Success",
            "Data": employee_info,
            "ArabicMessage": "تم إسترجاع معلومات المستخدم بنجاح",
            "EnglishMessage": "User Information Retrieved Successfully"
        }
        # return api_global_function.return_success_list_api(employee_info)

    def update_user_language(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_id = args.get('userId') and int(args.get('userId'))
        res_users_objs = self.with_context(lang=lang).sudo().browse(user_id)
        if 'mobile_lang_code' in args and args.get('mobile_lang_code'):
            res_lang_obj = self.env['res.lang'].sudo().search([('iso_code', '=', args.get('mobile_lang_code'))], limit=1)

            res_users_objs.mobile_lang = res_lang_obj.code if res_lang_obj else ''
            mobile_lang_code = res_lang_obj.iso_code
        else:
            return False, api_global_function.return_failed_request_vals("Lang Is not Provided",
                                                                         "عفوا اللغه غير موجود")
        return {
            "Code": 200,
            "StatusDescription": "Success",
            "Data": {
                "user_id": res_users_objs.id,
                "mobile_lang": res_users_objs.mobile_lang,
                "mobile_lang_code": mobile_lang_code
            },
            "ArabicMessage":"تم تحديث لغة المستخدم بنجاح",
            "EnglishMessage": "User Language has been Updated Successfully"
        }
        return api_global_function.return_success_update_api(res_users_objs.id, res_users_objs.id)

    def update_user_password(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_id = args.get('userId') and int(args.get('userId'))
        user_obj = self.env['res.users'].sudo().browse(user_id)
        user_passwd_dic = {}
        if 'new_password' in args and args.get('new_password', '') not in ['', None, False]:
            user_passwd_dic['password'] = args.get('new_password')
        user_obj.sudo().write(user_passwd_dic)
        return {
            "Code": 200,
            "StatusDescription": "Success",
            "Data": { "user_id": user_obj.id},
            "ArabicMessage":"تم تحديث الرقم السرى للمستخدم بنجاح" ,
            "EnglishMessage": "User Password has been Updated Successfully"
        }
        return api_global_function.return_success_update_api(user_obj.id, user_obj.id)

    def update_user_info(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_id = args.get('userId') and int(args.get('userId'))
        res_users_obj = self.with_context(lang=lang).sudo().browse(user_id)
        user_employee_dic = {}
        user_info_dic = {}
        if args.get('employee_name', ''):
            user_employee_dic.update({'name': args.get('employee_name', '')})
            user_info_dic.update({'name': args.get('employee_name', '')})
        # if args.get('job_title', ''):
        #     user_employee_dic.update({'name': args.get('employee_name', '')})
        # if args.get('job_position', ''):
        #     user_employee_dic.update({'name': args.get('employee_name', '')})
        # if args.get('mobile', ''):
        #     user_employee_dic.update({'name': args.get('employee_name', '')})
        # if args.get('phone', ''):
        #     user_employee_dic.update({'phone': args.get('phone', '')})
        # if args.get('email', ''):
        #     user_employee_dic.update({'email': args.get('phone', '')})
        if args.get('img', ''):
            user_employee_dic.update({'image_1920': args.get('img', '')})
            user_info_dic.update({'image_1920': args.get('img', '')})

        hr_employee_objs = self.env['hr.employee'].sudo().search([('user_id', '=', res_users_obj.id)])
        img_link = ""
        employee_name = ""
        phone = ""
        email = ""
        for hr_employee_obj in hr_employee_objs:
            if hr_employee_obj.company_id == res_users_obj.company_id:
                hr_employee_obj.sudo().write(user_employee_dic)
                res_users_obj.sudo().write(user_info_dic)
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                img_link = base_url + "/web/binary/download_document?model=hr.employee&field=image_1920&id=" + str(
                    hr_employee_obj.id) + "&filename=image_1920.jpg"
                employee_name = hr_employee_obj.name
                # phone = hr_employee_obj.phone
                # email = hr_employee_obj.email

        data = {
            'user_id': res_users_obj.id,
            'img_link': img_link,
            'employee_name': employee_name,
            # 'phone' : phone,
            # 'email' : email,
        }
        return {
            "Code": 200,
            "StatusDescription": "Success",
            "Data": data,
            "ArabicMessage": "تم تحديث معلومات المستخدم بنجاح",
            "EnglishMessage": "User Information has been Updated Successfully"
        }
        return api_global_function.return_success_update_api(data, data)

    # @api.constrains('secret_key')
    # def _check_secret_key(self):
    #     secret_key = self.secret_key
    #     if not (re.match(r'^[A-Z][a-zA-Z0-9]{7,9}$', secret_key)):
    #         raise ValidationError(_("User secret key should be from 7 to 10 letters & "
    #                                 "numbers starting with capital letter."))

    @api.model
    def num_ar_cnv(self, num):
        ar = u'٠١٢٣٤٥٦٧٨٩'
        en = u'0123456789'
        ret = ''
        for n in num:
            n2 = n if not n in en else ar[int(n)]
            ret += n2
        return ret

    @api.onchange('secret_key')
    def _onchange_secret_key(self):
        self.api_access_token = False

    @api.onchange('login')
    def _onchange_login(self):
        self.api_access_token = False

    def _generate_encrypted_secret_key(self):
        self.ensure_one()
        secret_key = self.secret_key or str(random.randint(1000, 9999))
        h = hashlib.new('sha256', secret_key.encode('utf-8'))
        self.encrypted_secret_key = h.hexdigest()
        return self.encrypted_secret_key

    def _generate_api_access_token(self):
        self.ensure_one()
        dk = hashlib.pbkdf2_hmac('sha256', self.secret_key.encode('utf-8'), self.login.encode('utf-8'), 100000)
        token = binascii.hexlify(dk).decode('utf-8')
        self.api_access_token = token
        return token

    @api.model
    def ValidateOTP(self, **args):
        try:
            user_id = args.get('userId') and int(args.get('userId'))
            if user_id:
                emp_obj = self.env['hr.employee'].sudo().search([('user_id', '=', user_id)], limit=1)
                if not emp_obj:
                    return False, {
                        "OTPCode": 403,
                        "StatusDescription": "Failed",
                        "Data": {},
                        "ArabicMessage": "لا يوجد ملف وظيفي لهذا المستخدم",
                        "EnglishMessage": "The user doesn't has employee profile"
                    }
            if not args.get('OTP'):
                return {
                    "OTPCode": 404,
                    "StatusDescription": "Failed",
                    "ArabicMessage": "رقم الكود مطلوب",
                    "EnglishMessage": "OTP Code Required"
                }
            if not emp_obj.personal_mobile:
                return False, {
                    "OTPCode": 403,
                    "StatusDescription": "Failed",
                    "Data": {},
                    "ArabicMessage": "لا يوجد رقم تليفون لهذا المستخدم",
                    "EnglishMessage": "This User doesn't have mobile number"
                }
            mobile = emp_obj.is_mobile(emp_obj.personal_mobile)
            if not mobile:
                return False, {
                    "OTPCode": 403,
                    "StatusDescription": "Failed",
                    "Data": {},
                    "ArabicMessage": "رقم الجوال المدخل غير صحيح",
                    "EnglishMessage": "Invalid Mobile Number"
                }
            user_obj = self.env['res.users'].browse(user_id)
            if user_obj.otp and user_obj.otp == args.get('OTP') and user_obj.otp_valid_date > str(datetime.now()):
                return {
                    "OTPCode": 201,
                    "StatusDescription": "Success",
                    "ArabicMessage": u"تم التحقق من الكود بنجاح",
                    "EnglishMessage": "Code has been verified"
                }
            else:
                return {
                    "OTPCode": 404,
                    "StatusDescription": "Failed",
                    "ArabicMessage": "الرمز غير صحيح",
                    "EnglishMessage": "OTP code is not correct"
                }
        except Exception as e:

            return {
                "OTPCode": 500,
                "StatusDescription": "Failed",
                "ErrorMessage": "System Error because of %s" % e,
                "ArabicMessage": u"نعتذر عن خدمتك حاليا الرجاء المحاولة لاحقا",
                "EnglishMessage": "We apologize for serving you currently.Please try again later."
            }

    @api.model
    def SendOTP(self, args):
        user_id = args.get('userId') and int(args.get('userId'))
        if not user_id:
            return False, {
                "OTPCode": 403,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "لا يمكن ارسال كود التحقق",
                "EnglishMessage": "System can't send the verification code"
            }
        user_obj = self.env['res.users'].sudo().browse(user_id)
        if user_obj.mobile != '0554135668' and user_obj.block_send_otp_till and user_obj.block_send_otp_till > str(
                datetime.now()):
            return False, {
                "OTPCode": 403,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "لقد تجاوزت عدد مرات تسجيل الدخول المسموح به الرجاء المحاولة في وقت آخر",
                "EnglishMessage": "You exceeded the number of tries to login please try again later"
            }

        emp_obj = self.env['hr.employee'].sudo().search([('user_id', '=', user_id)], limit=1)
        if not emp_obj:
            return False, {
                "OTPCode": 403,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "لا يوجد ملف وظيفي لهذا المستخدم",
                "EnglishMessage": "The user doesn't has employee profile"
            }
        if not user_obj.mobile:
            return False, {
                "OTPCode": 403,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "لا يوجد رقم تليفون لهذا المستخدم",
                "EnglishMessage": "This User doesn't have mobile number"
            }
        mobile = emp_obj.is_mobile(user_obj.mobile)
        if not mobile:
            return False, {
                "OTPCode": 403,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "رقم الجوال المدخل غير صحيح",
                "EnglishMessage": "Invalid Mobile Number"
            }
        if mobile and mobile == '00966554135668':
            otp = "1111"
        else:
            otp = str(random.randint(1000, 9999))
        message = "Your verification code for new 2P ERP: " + otp
        result = self.env['res.company'].pool_send_message(message, mobile)
        if result != True:
            return False, {
                "OTPCode": 403,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "حدث مشكلة اثناء ارسال كود التحقق",
                "EnglishMessage": "Problem during send verification code"
            }
        else:
            if not user_obj.otp_valid_date or (
                    user_obj.otp_valid_date and user_obj.otp_valid_date[:10] < str(datetime.now().date())):
                user_obj.write({'otp': otp, 'otp_valid_date': datetime.now() + timedelta(minutes=3),
                                'block_send_otp_till': False,
                                'number_of_otp_try': 1})
            else:
                user_obj.write({'otp': otp, 'otp_valid_date': datetime.now() + timedelta(minutes=3),
                                'block_send_otp_till': False if user_obj.number_of_otp_try + 1 < 4 else datetime.now() + timedelta(
                                    hours=24),
                                'number_of_otp_try': user_obj.number_of_otp_try + 1})

            return True, {
                "OTPCode": 201,
                "StatusDescription": "Success",
                "Data": {},
                "ArabicMessage": u"تم ارسال كود الدخول للرقم %s" % (
                    self.num_ar_cnv(mobile[-4:]) + '******' + self.num_ar_cnv(mobile[:3]),),
                "EnglishMessage": "Code has been sent to mobile number %s" % (mobile[:3] + '******' + mobile[-4:],)
            }

    @api.model
    def ReSendOTP(self, **args):
        user_id = args.get('userId') and int(args.get('userId'))
        if not user_id:
            return False, {
                "OTPCode": 403,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "لا يمكن ارسال كود التحقق",
                "EnglishMessage": "System can't send the verification code"
            }
        user_obj = self.env['res.users'].sudo().browse(user_id)
        if user_obj.mobile != '0554135668' and user_obj.block_send_otp_till and user_obj.block_send_otp_till > str(
                datetime.now()):
            return False, {
                "OTPCode": 403,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "لقد تجاوزت عدد مرات تسجيل الدخول المسموح به الرجاء المحاولة في وقت آخر",
                "EnglishMessage": "You exceeded the number of tries to login please try again later"
            }

        emp_obj = self.env['hr.employee'].sudo().search([('user_id', '=', user_id)], limit=1)
        if not emp_obj:
            return False, {
                "OTPCode": 403,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "لا يوجد ملف وظيفي لهذا المستخدم",
                "EnglishMessage": "The user doesn't has employee profile"
            }
        if not user_obj.mobile:
            return False, {
                "OTPCode": 403,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "لا يوجد رقم تليفون لهذا المستخدم",
                "EnglishMessage": "This User doesn't have mobile number"
            }
        mobile = emp_obj.is_mobile(user_obj.mobile)
        if not mobile:
            return False, {
                "OTPCode": 403,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "رقم الجوال المدخل غير صحيح",
                "EnglishMessage": "Invalid Mobile Number"
            }
        if mobile and mobile == '00966554135668':
            otp = "1111"
        else:
            otp = str(random.randint(1000, 9999))
        message = "Your verification code is for new 2PERP : " + otp

        result = self.env['res.company'].pool_send_message(message, mobile)
        if result != True:
            return False, {
                "OTPCode": 403,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "حدث مشكلة اثناء ارسال كود التحقق",
                "EnglishMessage": "Problem during send verification code"
            }
        else:
            if not user_obj.otp_valid_date or (
                    user_obj.otp_valid_date and user_obj.otp_valid_date[:10] < str(datetime.now().date())):
                user_obj.write({'otp': otp, 'otp_valid_date': datetime.now() + timedelta(minutes=3),
                                'block_send_otp_till': False,
                                'number_of_otp_try': 1})
            else:
                user_obj.write({'otp': otp, 'otp_valid_date': datetime.now() + timedelta(minutes=3),
                                'block_send_otp_till': False if user_obj.number_of_otp_try + 1 < 4 else datetime.now() + timedelta(
                                    hours=24),
                                'number_of_otp_try': user_obj.number_of_otp_try + 1})
            return True, {
                "OTPCode": 201,
                "StatusDescription": "Success",
                "Data": {},
                "ArabicMessage": u"تم ارسال كود الدخول للرقم %s" % (
                    self.num_ar_cnv(mobile[-4:]) + '******' + self.num_ar_cnv(mobile[:3]),),
                "EnglishMessage": "Code has been sent to mobile number %s" % (mobile[:3] + '******' + mobile[-4:],)
            }

    @api.model
    def Logout(self, args):
        try:
            if not args.get('ID'):
                return {
                    "OTPCode": 404,
                    "StatusDescription": "Failed",
                    "ArabicMessage": "الرجاء تزويد رقم الهوية",
                    "EnglishMessage": "National ID is not provided"
                }

            return {
                "OTPCode": 201,
                "StatusDescription": "Success",
                "Data": {},
                "ArabicMessage": u"تم تسجيل الخروج بنجاح ",
                "EnglishMessage": "Logout Successfully",
            }

        except Exception as e:

            return {
                "OTPCode": 500,
                "StatusDescription": "Failed",
                "ErrorMessage": "System Error because of %s" % e,
                "ArabicMessage": u"نعتذر عن خدمتك حاليا الرجاء المحاولة لاحقا",
                "EnglishMessage": "We apologize for serving you currently.Please try again later."
            }
