# -*- coding: utf-8 -*-
""" Odoo Rest Api Integration"""

from odoo import http, _, models
from odoo.exceptions import AccessDenied
from odoo.http import request, content_disposition
from odoo.tools import image_process
import hashlib, base64
import ast


def _generate_encrypted_secret_key(secret_key):
    h = hashlib.new('sha256', secret_key.encode('utf-8'))
    encrypted_secret_key = h.hexdigest()
    return encrypted_secret_key


def _check_authenticated_user():
    if not request.httprequest.headers.get('Token'):
        raise Exception(_("Invalid Access Token"))
    access_token = request.httprequest.headers['Token']
    user = request.env['res.users'].sudo().search([('api_access_token', '=', access_token)])
    if not user:
        raise AccessDenied()

    return {
        'userId': user.id,
    }


class RestApi(http.Controller):
    """
    There are URIs available:

    /api/auth                   POST    - Login in Odoo

    /api/<model>                GET     - Read all (with optional domain, fields, offset, limit, order)
    /api/<model>/<id>           GET     - Read one (with optional fields)
    /api/<model>                POST    - Create one
    /api/<model>/<id>           POST     - Update one
    /api/<model>/<id>           DELETE  - Delete one
    /api/<model>/<id>/<method>  POST     - Call method (with optional parameters)
    /api/<model>/<method>  POST     - Call method (with optional parameters)
    /api/<model>/<method>  GET     - Call method (with optional parameters)
    """

    def check_addon_state(self, addon_name):
        ir_module_objs = request.env['ir.module.module'].sudo().search(
            [('name', '=', addon_name), ('state', '=', 'installed')])
        if ir_module_objs:
            return True
        else:
            return False

    @http.route('/web/binary/download_document', type='http', auth="public")
    def download_document(self, model, field, id, filename=None, **kw):
        """ Download link for files stored as binary fields.
        :param str model: name of the model to fetch the binary from
        :param str field: binary field
        :param str id: id of the record from which to fetch the binary
        :param str filename: field holding the file's name, if any
        :returns: :class:`werkzeug.wrappers.Response`
        """
        Model = request.registry[model]
        cr, uid, context = request.cr, request.uid, request.context
        fields = [field]
        model_obj = request.env[model].sudo().browse(int(id))
        if not field:
            return request.not_found()
        if field:
            field_date = model_obj.read(fields=[field])
        # model_obj = request.env['insurance.type'].sudo().read(fields=[field])
        filecontent = base64.b64decode(field_date[0][field] or '')
        if not filecontent:
            return request.not_found()
        else:
            # filename = '%s_%s' % (model.replace('.', '_'), id)
            return request.make_response(filecontent,
                                         [('Content-Type', 'application/octet-stream'),
                                          ('Content-Disposition', content_disposition(filename))])

    @http.route('/get_app_info', type='json', auth='public', methods=['GET', 'POST'], csrf=False, cors='*',
                website=True)
    def get_app_info(self, **args):
        res_company_obj = request.env['res.company'].sudo().browse(1)
        # res_config_settings_obj = request.env['res.config.settings'].sudo().search([('company_id','=',1)], limit=1)
        xyz = {
            "Code": 200,
            'Data': [{'app_name': res_company_obj.app_name or '',
                      'app_version': res_company_obj.app_version,
                      'app_store_app_link': res_company_obj.app_store_app_link or '',
                      'google_play_app_link': res_company_obj.google_play_app_link or '',
                      }],
            "StatusDescription": "Success",
            "ArabicMessage": "تم استرجاع المعلومات بنجاح",
            "EnglishMessage": "App Information returned Successfully ",
        }
        return xyz

    @http.route('/login_user_account', auth='none', type="json", methods=["POST"], csrf=False)
    def authenticate(self, db, login, password, base_location=None):
        # db = configparser['api_db_name']
        authenticate_test = request.session.authenticate(db, login, password)
        session_info = request.session
        # return session_info
        # session_info = request.env['ir.http'].sudo().session_info()
        if 'uid' in session_info and session_info.get('uid') not in [False, None]:
            uid = session_info.get('uid')
        elif 'pre_uid' in session_info and session_info.get('pre_uid') not in [False, None]:
            uid = session_info.get('pre_uid')
        else:
            session_info.update({
                "Code": 404,
                "StatusDescription": "Failed",
                "ArabicMessage": "عفوا البيانات المدخلة خاطئة",
                "EnglishMessage": "Invalid Username or password"
            })
        user = request.env['res.users'].sudo().browse(uid)
        token = user.api_access_token
        if not token:
            token = user.sudo()._generate_api_access_token()
        hr_employee_objs = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)])
        img_link = ""

        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        employee_info = {}
        for hr_employee_obj in hr_employee_objs:
            if hr_employee_obj.company_id == user.company_id:
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
        fcm_tokens = []
        for mail_firebase_tokens_obj in user.sudo().partner_id.sudo().mail_firebase_tokens:
            fcm_tokens.append(
                {
                    'fcm_token_id': mail_firebase_tokens_obj.id,
                    'user_id': mail_firebase_tokens_obj.user_id.id,
                    'user_name': mail_firebase_tokens_obj.user_id.name,
                    'name': mail_firebase_tokens_obj.os,
                    'fsm_token': mail_firebase_tokens_obj.token
                }
            )
        session_info['project'] = self.check_addon_state('project')
        session_info['meeting'] = self.check_addon_state('calendar')
        session_info['attendance'] = self.check_addon_state('hr_attendance')
        session_info['loan'] = self.check_addon_state('ent_loan_accounting')
        session_info['timeoff'] = self.check_addon_state('hr_holidays')
        xyz = {
            "Code": 200,
            'mobile_lang': user.mobile_lang,
            'mobile_lang_code': request.env['res.lang'].search([('code', '=', user.mobile_lang)]).iso_code,
            'token': token,
            'company_id': user.company_id.id,
            'company_name': user.company_id.name,
            'currency_id': user.company_id.currency_id.id,
            'currency_name': user.company_id.currency_id.name,
            'context': session_info['context'],
            "db": session_info['db'] if 'db' in session_info else '',
            "debug": session_info['debug'] if 'debug' in session_info else '',
            "login": session_info['login'] if 'login' in session_info else '',
            "uid": session_info['uid'] if 'uid' in session_info else '',
            "session_token": session_info['session_token'] if 'session_token' in session_info else '',
            "profile_session": session_info['profile_session'] if 'profile_session' in session_info else '',
            "profile_collectors": session_info['profile_collectors'] if 'profile_collectors' in session_info else '',
            "profile_params": session_info['profile_params'] if 'profile_params' in session_info else '',

            "_geoip": session_info['_geoip'] if '_geoip' in session_info else '',
            'fcm_tokens': fcm_tokens,
            "StatusDescription": "Success",
            "ArabicMessage": "تم تسجيل الدخول بنجاح",
            "EnglishMessage": "Login Successfully",
        }
        return xyz

    # @http.route('/web/session/erp_authenticate', type='json', auth="none")
    # def erp_authenticate(self, db, login, password, base_location=None):
    #     request.session.authenticate(db, login, password)
    #     session_info = request.env['ir.http'].session_info()
    #     if 'uid' in session_info and session_info.get('uid') != False:
    #         user = request.env['res.users'].sudo().browse(session_info.get('uid'))
    #         token = user.api_access_token
    #         if not token:
    #             token = user.sudo()._generate_api_access_token()
    #         session_info.update({'token':token,"Code": 200,"StatusDescription": "Failed",
    #                                "ArabicMessage": "تم تسجيل الدخول بنجاح",
    #                                "EnglishMessage": "Login Successfully"
    #                                })
    #         result, result_dic = user.SendOTP({'token': token, 'userId': user.id,'OTPDetails':{}})
    #         if result:
    #             session_info.update({'OTPDetails':result_dic})
    #     else:
    #         session_info.update({
    #                             "Code":404,
    #                             "StatusDescription": "Failed",
    #                             "ArabicMessage": "عفوا البيانات المدخلة خاطئة",
    #                             "EnglishMessage": "Invalid Username or password"
    #                              })
    #     return session_info
    #
    #
    # @route('/api/auth', auth='none', type="json", methods=["POST"], csrf=False)
    # @make_response()
    # def authenticate(self):
    #     data = request.httprequest.data.decode('utf-8')
    #     data = ast.literal_eval(data)
    #     if not data:
    #         raise Exception("Invalid login data")
    #     # eval_request_params(data)
    #     lang = request.httprequest.headers.get('lang') or 'en'
    #     if lang not in ['ar', 'en']:
    #         raise Exception("Invalid Application Language")
    #     lang = 'ar_AA' if lang == 'ar' else 'en_US'
    #     login = 'userName' in data and str(data['userName'])
    #     secret_key = 'secretKey' in data and str(data['secretKey'])
    #     if not (login and secret_key):
    #         raise UserError(_("Invalid login data"))
    #
    #     # try:
    #     #     secret_key = base64.b64decode(secret_key).decode('utf-8')
    #     # except Exception:
    #     #     raise AccessDenied()
    #
    #     encrypted_key = _generate_encrypted_secret_key(secret_key)
    #
    #     user = request.env['res.users'].sudo().search([('login', '=', login),
    #                                                   ('encrypted_secret_key', '=', encrypted_key)])
    #     if not user:
    #         raise AccessDenied()
    #     token = user.api_access_token
    #     if not token:
    #         token = user.sudo()._generate_api_access_token()
    #     result, result_dic = user.SendOTP({'token': token, 'userId':user.id})
    #     if result:
    #         return result_dic.update({'token': token, 'status':200,})
    #     else:
    #         return result_dic
    #
    @http.route(['/api/<string:model>',
                 '/api/<string:model>/<int:id>'],
                type="json", auth='none', methods=["GET"], csrf=False)
    def search_read_record(self, model, id=None):
        """ Read all records or a specific record with optional domain, fields, offset,
         limit & order. """
        _check_authenticated_user()
        if not request.env['ir.model'].sudo().search([('model', '=', model)]):
            raise Exception('There is no model named %s' % model)
            data = dict()
        if request.httprequest.args:
            data = request.httprequest.args.to_dict()
        # eval_request_params(data)
        keys = ['domain', 'fields', 'offset', 'limit', 'order']
        for key in data.keys():
            if key not in keys:
                raise Exception("unexpected argument %s", key)
        if id:
            record = request.env[model].sudo().search([('id', '=', id)])
            if not record:
                raise Exception('There is no record with id %s' % str(id))
            result = record.sudo().read(**data)
            result = result and result[0] or {}
            return result
        return request.env[model].sudo().search_read(**data)

    @http.route(['/api/<string:model>',
                 '/api/<string:model>/<int:id>'], type='json', auth="none",
                methods=["POST"], csrf=False)
    def create_update_record(self, model, id=None):
        """ create or update a record of a model. """
        _check_authenticated_user()
        if not request.env['ir.model'].sudo().search([('model', '=', model)]):
            raise Warning('There is no model named %s' % model)
        data = request.httprequest.data.decode('utf-8')
        data = ast.literal_eval(data)
        if not data:
            raise Exception("Invalid record data")
        # eval_request_params(data)
        fields = request.env[model].sudo().fields_get().keys()
        for key in data.keys():
            if key not in fields:
                raise Warning('There is no attribute named %s' % key)
        if id:
            record = request.env[model].sudo().search([('id', '=', id)])
            if not record:
                raise Exception('There is no record with id %s' % str(id))
            result = record.sudo().write(data)
            return result and 'Record with id %s successfully updated ' % str(id)
        spec = request.env[model]._onchange_spec()
        updates = request.env[model].sudo().onchange(data, list(fields), spec)
        values = updates.get('value', {})
        values = {k: v for k, v in values.items() if v}
        for name, val in values.items():
            if isinstance(val, tuple):
                values[name] = val[0]
        data.update(values)
        result = request.env[model].sudo().create(data)
        if result:
            return {
                "id": result.id,
                "message": 'Record created successfully with id %s' % str(result.id)
            }

    @http.route('/api/<string:model>/<int:id>', auth='none', type="json", methods=["DELETE"])
    def unlink(self, model, id):
        """ Delete a record of a model if found. """
        _check_authenticated_user()
        if not request.env['ir.model'].sudo().search([('model', '=', model)]):
            raise Exception('There is no model named %s' % model)
        record = request.env[model].sudo().search([('id', '=', id)])
        if not record:
            raise Exception('There is no record with id %s' % str(id))
        record.sudo().unlink()
        return {
            "id": id,
            "message": 'Record with id %s  deleted successfully' % str(id)
        }

    @http.route(['/api/<string:model>/<int:id>/<string:method>',
                 '/api/<string:model>/<string:method>'], auth='none',
                methods=["POST"], type='json', csrf=False)
    def record_method(self, model, method, id=None, **kwargs):
        lang = request.httprequest.headers.get('lang') or 'en'
        if lang not in ['ar', 'en']:
            raise Exception("Invalid Application Language")
        if not request.env['ir.model'].sudo().search([('model', '=', model)]):
            raise Exception('There is no model named %s' % model)

        record = request.env[model].sudo().search([('id', '=', id)])
        data = request.httprequest.data.decode('utf-8')
        data = ast.literal_eval(data)
        # eval_request_params(data)
        data['lang'] = lang
        user_dict = _check_authenticated_user()
        data.update(user_dict)
        if record:
            method = getattr(record, method)
            return method(**data)
        return getattr(request.env[model], method)(**data)

    @http.route('/api/<string:model>/<string:method>', auth='none', methods=["GET"], type='json', csrf=False)
    def model_method(self, model, method):
        url_params = dict()
        lang = request.httprequest.headers.get('lang') or 'en'
        if lang not in ['ar', 'en']:
            raise Exception("Invalid Application Language")
        url_params['lang'] = lang
        if not request.env['ir.model'].sudo().search([('model', '=', model)]):
            raise Exception('There is no model named %s' % model)
        if request.httprequest.args:
            args = request.httprequest.args.to_dict()
            url_params.update(args)
        user_dict = _check_authenticated_user()
        url_params.update(user_dict)
        return getattr(request.env[model], method)(**url_params)
