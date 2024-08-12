from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging
from datetime import datetime

from odoo.exceptions import ValidationError
from . import api_global_function

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class crm_salesperson_planner_visit(models.Model):
    _inherit = "crm.salesperson.planner.visit"

    duration = fields.Char('Duration', compute="calc_visit_duration")
    start_datetime = fields.Datetime('From')
    start_location = fields.Char('Location')
    start_lat = fields.Char('Lat')
    start_long = fields.Char('Long')

    end_datetime = fields.Datetime('To')
    end_location = fields.Char('Location')
    end_lat = fields.Char('Lat')
    end_long = fields.Char('Long')

    @api.depends('end_datetime', 'start_datetime')
    @api.onchange('end_datetime', 'start_datetime')
    def calc_visit_duration(self):
        for record in self:
            end_datetime = datetime.now()
            record.duration = ""
            if record.end_datetime:
                end_datetime = record.end_datetime
            if record.start_datetime:
                record.duration = end_datetime - record.start_datetime

    def get_partner_visits(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_id = args.get('userId') and int(args.get('userId'))
        domain = []
        # if args.get('my_visit', False) == True:
        #     domain.append(('user_id', '=', user_id))
        domain = [('user_id', '=', user_id)]
        try:
            if args.get("visit_id", False):
                if not self.sudo().search([('id', '=', int(args.get('visit_id', False)))]):
                    return False, api_global_function.return_failed_request_vals("The Visit not exist",
                                                                                 "عفوا الزيارة غير موجود")
                domain.append(('id', '=', args.get("visit_id", False)))
            if args.get("visit_date", False):
                domain.append(('date', '<=', args.get("visit_date", False)))
                domain.append(('date', '>=', args.get("visit_date", False)))
            if args.get("client_id", False):
                if not self.env['res.partner'].sudo().search([('id', '=', int(args.get('client_id', False)))]):
                    return False, api_global_function.return_failed_request_vals("The Partner not exist profile",
                                                                                 "عفوا العميل غير موجود")
                domain.append(('partner_id', '=', args.get("client_id", False)))
            crm_visits_objs = self.with_context(lang=lang).sudo().search(domain)
            crm_visits = []
            for crm_visits_obj in crm_visits_objs:
                crm_visits.append(
                    {
                        'visit_id': crm_visits_obj.id,
                        'visit_date': crm_visits_obj.date or "",
                        'client_id': crm_visits_obj.partner_id.id or "",
                        'client_name': crm_visits_obj.partner_id.name or "",
                        'phone': crm_visits_obj.partner_phone or "",
                        'mobile': crm_visits_obj.partner_phone or "",
                        'salesperson_id': crm_visits_obj.user_id.id,
                        'salesperson_name': crm_visits_obj.user_id.name,
                        'description': crm_visits_obj.description or "",
                        'start_datetime': crm_visits_obj.start_datetime or "",
                        'start_location': crm_visits_obj.start_location or "",
                        'start_lat': crm_visits_obj.start_lat or "",
                        'start_long': crm_visits_obj.start_long or "",
                        'end_datetime': crm_visits_obj.end_datetime or "",
                        'end_location': crm_visits_obj.end_location or "",
                        'end_lat': crm_visits_obj.end_lat or "",
                        'end_long': crm_visits_obj.end_long or "",
                        'state': dict(crm_visits_obj._fields['state'].selection).get(crm_visits_obj.state),
                        'duration': crm_visits_obj.duration or "",
                    }
                )
        except Exception as e:
            arabic_message = "%s  " % _(str(e))
            englishmessage = "%s." % _(str(e))
            return api_global_function.return_failed_request_vals(englishmessage, arabic_message)
        return api_global_function.return_success_list_api(crm_visits)

    def check_visit(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_id = args.get('userId') and int(args.get('userId'))
        try:
            res_user_obj = self.env['res.users'].sudo().browse(user_id)
            if not args.get('client_id', False):
                return False, api_global_function.return_failed_request_vals("Customer ID Not provided",
                                                                             "عفوا العميل مش موجود")
            if not self.env['res.partner'].sudo().search([('id', '=', args.get('client_id', False))]):
                return False, api_global_function.return_failed_request_vals("Customer ID Not Correct",
                                                                             "عفوا العميل غير صحيح")
            res_partner_obj = self.env['res.partner'].sudo().browse(int(args.get('client_id', False)))
            partner_visit_obj = self.with_context(lang=lang).sudo().search(
                [('user_id', '=', user_id), ('partner_id', '=', int(args.get('client_id', '')))], order="id desc",
                limit=1)
            partner_id = ''
            partner_name = ''
            visit_status = "check_in"
            visit_id = partner_visit_obj.id
            date = ''
            location = ''
            lat = ''
            long = ''
            end_datetime = ""
            start_datetime = ""
            duration = ""
            if partner_visit_obj and partner_visit_obj.start_datetime and not partner_visit_obj.end_datetime:
                visit_status = "check_out"
                start_datetime = partner_visit_obj.start_datetime
                end_datetime = partner_visit_obj.end_datetime
                partner_id = res_partner_obj.id
                partner_name = res_partner_obj.display_name
                visit_id = partner_visit_obj.id
                location = partner_visit_obj.start_location
                lat = partner_visit_obj.start_lat
                long = partner_visit_obj.start_long
                duration = partner_visit_obj.duration
            if not partner_visit_obj or (
                    partner_visit_obj and partner_visit_obj.start_datetime and partner_visit_obj.end_datetime):
                visit_status = "check_in"
                start_datetime = partner_visit_obj.start_datetime
                end_datetime = partner_visit_obj.end_datetime
                partner_id = res_partner_obj.id
                partner_name = res_partner_obj.display_name
                visit_id = ''
                location = ''
                lat = ''
                long = ''
                duration = partner_visit_obj.duration if partner_visit_obj else ''
            visit_info = {
                "client_id": partner_id or '',
                "client_name": partner_name or '',
                "start_datetime": start_datetime or '',
                "end_datetime": end_datetime or '',
                'location': location,
                "lat": lat or " ",
                'long': long or " ",
                'visit_status': visit_status,
                'visit_id': visit_id,  # for adding checkout value
                'duration': duration,
            }
        except Exception as e:
            arabic_message = "%s  " % _(str(e))
            englishmessage = "%s." % _(str(e))
            return api_global_function.return_failed_request_vals(englishmessage, arabic_message)
        return api_global_function.return_success_list_api(visit_info)

    def check_visit_vals(self, args):
        visit_vals = {}
        if args.get("visit_id", False):
            visit_vals.update({'id': args.get("RequestID", False)})
        try:
            if not args.get('client_id', False):
                return False, api_global_function.return_failed_request_vals("Customer ID Not provided",
                                                                             "عفوا العميل مش موجود")
            if not self.env['res.partner'].sudo().search([('id', '=', args.get('client_id', False))]):
                return False, api_global_function.return_failed_request_vals("Customer ID Not Correct",
                                                                             "عفوا العميل غير صحيح")
            if not args.get("visit_status", False):
                return False, api_global_function.return_failed_request_vals("Visit Status Not provided",
                                                                             "عفوا نوع الزيارة مش موجود")
            if args.get("visit_status", False) and args.get("visit_status", False) not in ['check_in', 'check_out']:
                return False, api_global_function.return_failed_request_vals("Visit Status Not Correcr",
                                                                             "عفوا نوع الزيارة غير صحيح")
            if not args.get('lat', False):
                return False, api_global_function.return_failed_request_vals("Visit Lat Not provided",
                                                                             "عفوا احداثيات الزيارة مش موجود")
            if not args.get('long', False):
                return False, api_global_function.return_failed_request_vals("Visit Long Not provided",
                                                                             "عفوا احداثيات الزيارة مش موجود")
            if not args.get('location', False):
                return False, api_global_function.return_failed_request_vals("Visit Location Not provided",
                                                                             "عفوا عنوان الزيارة مش موجود")
            datetime.now().strptime(str((datetime.now()).strftime("%Y-%m-%d %H:%M:%S")), "%Y-%m-%d %H:%M:%S")
            if args.get("visit_status", False) == 'check_in':
                visit_vals.update({'date': str(datetime.now().date())})
                visit_vals.update({'state': 'confirm'})
                visit_vals.update({'start_location': args.get('location', False)})
                visit_vals.update({'start_lat': args.get('lat', False)})
                visit_vals.update({'start_long': args.get('long', False)})
                visit_vals.update({'start_datetime': str(
                    datetime.now().strptime(str((datetime.now()).strftime("%Y-%m-%d %H:%M:%S")), "%Y-%m-%d %H:%M:%S"))})
            elif args.get("visit_status", False) == 'check_out':
                visit_vals.update({'state': 'done'})
                visit_vals.update({'end_location': args.get('location', False)})
                visit_vals.update({'end_lat': args.get('lat', False)})
                visit_vals.update({'end_long': args.get('long', False)})
                visit_vals.update({'end_datetime': str(
                    datetime.now().strptime(str((datetime.now()).strftime("%Y-%m-%d %H:%M:%S")), "%Y-%m-%d %H:%M:%S"))})
            visit_vals.update({'partner_id': args.get("client_id", False)})



        except Exception as e:
            arabic_message = "%s  " % _(str(e)),
            englishmessage = "%s." % _(str(e))
            return False, api_global_function.return_failed_request_vals(englishmessage, arabic_message)
        return True, visit_vals

    def add_visit_for_client(self, **args):
        request_id = args.get("visit_id", False)
        check_vals, visit_vals = self.check_visit_vals(args)
        if not check_vals:
            return visit_vals
        try:
            if not request_id:
                res_partner_visit_obj = self.with_user(args.get('userId')).sudo().create(visit_vals)
            else:
                # Update Request ID
                res_partner_visit_obj = self.with_user(args.get('userId')).sudo().browse(request_id)
                res_partner_visit_obj.with_user(args.get('userId')).sudo().write(visit_vals)
        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        visit_dic = {
            'visit_id': res_partner_visit_obj.id,
            'visit_date': res_partner_visit_obj.date or '',
            'client_id': res_partner_visit_obj.partner_id.id,
            'client_name': res_partner_visit_obj.partner_id.name,
            'phone': res_partner_visit_obj.partner_phone or '',
            'mobile': res_partner_visit_obj.partner_phone or '',
            'salesperson_id': res_partner_visit_obj.user_id.id,
            'salesperson_name': res_partner_visit_obj.user_id.name,
            'description': res_partner_visit_obj.description or '',
            'start_datetime': res_partner_visit_obj.start_datetime or '',
            'start_location': res_partner_visit_obj.start_location or '',
            'start_lat': res_partner_visit_obj.start_lat or '',
            'start_long': res_partner_visit_obj.start_long or '',
            'end_datetime': res_partner_visit_obj.end_datetime or '',
            'end_location': res_partner_visit_obj.end_location or '',
            'end_lat': res_partner_visit_obj.end_lat or '',
            'end_long': res_partner_visit_obj.end_long or '',
            'state': dict(res_partner_visit_obj._fields['state'].selection).get(res_partner_visit_obj.state),
            'duration': res_partner_visit_obj.duration,
        }
        if not request_id:
            return {
                "Code": 200,
                "StatusDescription": "Success",
                "Data": visit_dic,
                "ArabicMessage": "تم انشاء الطلب بنجاح رقم(%s)  " % str(res_partner_visit_obj.id),
                "EnglishMessage": "Request Number (%s)has been created successfully." % str(res_partner_visit_obj.id)
            }
            # return api_global_function.return_success_creation_api(visit_dic, visit_dic)
        else:
            return {
                "Code": 200,
                "StatusDescription": "Success",
                "Data": visit_dic,
                "ArabicMessage": "تم تعديل الطلب بنجاح رقم(%s)  " % str(res_partner_visit_obj.id),
                "EnglishMessage": "Request Number (%s)has been updated successfully." % str(res_partner_visit_obj.id)
            }
            # return api_global_function.return_success_update_api(visit_dic, visit_dic)

    def get_my_dashboard(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_id = args.get('userId') and int(args.get('userId'))
        # 1- visits
        my_visit_objs = self.with_context(lang=lang).sudo().search([('user_id', '=', user_id)])
        visit_status = {'uncompleleted': 0, 'compeleted': 0, 'all_visit': len(my_visit_objs), 'checked_in': 0,
                        'cancel': 0, 'incident': 0}
        for my_visit_obj in my_visit_objs:
            if my_visit_obj.state == 'draft':
                visit_status['uncompleleted'] += 1
            elif my_visit_obj.state == 'done':
                visit_status['compeleted'] += 1
            elif my_visit_obj.state == 'confirm':
                visit_status['checked_in'] += 1
            elif my_visit_obj.state == 'cancel':
                visit_status['cancel'] += 1
            elif my_visit_obj.state == 'incident':
                visit_status['incident'] += 1
        # 2- partner location
        res_partner_objs = self.env['res.partner'].sudo().search(
            ['|', ('partner_latitude', '!=', 0.0), ('partner_longitude', '!=', 0.0)]).read(
            ['id', 'name', 'partner_latitude', 'partner_longitude'])
        domain = [('create_date', '>=', '2023-01-01'), ('create_date', '<=', '2023-01-31')]
        fields = ['amount_total:sum']
        group_by = ['partner_id']
        account_move_objs = self.env['account.move'].sudo().read_group([], fields, group_by)

        dashboard = {
            'visits': visit_status,
            'map': res_partner_objs,
            'invoices': account_move_objs
        }
        return api_global_function.return_success_list_api(dashboard)
