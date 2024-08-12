from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging
from . import api_global_function
from odoo.tests import Form

_logger = logging.getLogger(__name__)


class crm_salesperson_planner_visit_goals(models.Model):
    _inherit = "crm.salesperson.planner.visit.goals"

    def get_state_name(self, state_name):
        if state_name == 'draft':
            return 'Goal'
        elif state_name == 'confirm':
            return 'Checked In'
        elif state_name == 'done':
            return 'Visited'
        elif state_name == 'cancel':
            return 'Cancelled'
        elif state_name == 'incident':
            return 'Incident'
        else:
            return ''

    def get_my_goals(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_id = args.get('userId') and int(args.get('userId'))
        domain = [('user_id', '=', user_id)]
        if args.get('goal_id', False):
            domain.append(('id','=',int(args.get('goal_id', False))))
        if args.get("goal_from_date", False):
            domain.append(('date', '<=', args.get("goal_from_date", False)))
            if args.get("goal_to_date", False):
                domain.append(('to_date', '>=', args.get("goal_to_date", False)))
        visit_goal_objs = self.with_context(lang=lang).sudo().search(domain, order="id desc")
        visit_goal = []
        for visit_goal_obj in visit_goal_objs:
            visit_goal_details = []
            for crmsalespersonplannervisitgoalsdetails_obj in visit_goal_obj.crmsalespersonplannervisitgoalsdetails_ids:
                visit_goal_details.append(
                    {
                        'goal_line_id': crmsalespersonplannervisitgoalsdetails_obj.id,
                        'goal_line_name': crmsalespersonplannervisitgoalsdetails_obj.name or '',
                        'goal_line_partner_id': crmsalespersonplannervisitgoalsdetails_obj.partner_id.id or '',
                        'goal_line_partner_name': crmsalespersonplannervisitgoalsdetails_obj.partner_id.name or '',
                        'goal_line_partner_phone': crmsalespersonplannervisitgoalsdetails_obj.partner_phone or '',
                        'goal_line_partner_mobile': crmsalespersonplannervisitgoalsdetails_obj.partner_mobile or '',
                        'goal_line_date': crmsalespersonplannervisitgoalsdetails_obj.date or '',
                        'goal_line_user_id': crmsalespersonplannervisitgoalsdetails_obj.user_id.id,
                        'goal_line_user_name': crmsalespersonplannervisitgoalsdetails_obj.user_id.name or '',
                        'goal_line_description': crmsalespersonplannervisitgoalsdetails_obj.description or '',
                        'goal_line_state': self.get_state_name(crmsalespersonplannervisitgoalsdetails_obj.state) ,
                        'goal_line_visit_id': crmsalespersonplannervisitgoalsdetails_obj.visit_id.id,
                        'goal_line_visit_name': crmsalespersonplannervisitgoalsdetails_obj.visit_id.name,
                        'goal_line_goal_id': crmsalespersonplannervisitgoalsdetails_obj.goal_id.id,
                        'goal_line_goal_name': crmsalespersonplannervisitgoalsdetails_obj.goal_id.name,
                    }
                )
            visit_goal.append({
                'goal_id': visit_goal_obj.id,
                'goal_name': visit_goal_obj.name or '',
                'goal_from_date': visit_goal_obj.date or '',
                'goal_to_date': visit_goal_obj.to_date or '',
                'goal_no_of_visits': visit_goal_obj.no_of_visits,
                'goal_user_id': visit_goal_obj.user_id.id,
                'goal_user_name': visit_goal_obj.user_id.name or '',
                'goal_details': visit_goal_details
            })
        return api_global_function.return_success_list_api(visit_goal)

    def check_visit_goal_vals(self, args):
        visit_goal_vals = {}
        if args.get("goal_id", False):
            visit_goal_vals.update({'id': args.get("goal_id", False)})
        visit_goal_vals.update({'user_id': args.get('userId') and int(args.get('userId'))})
        visit_goal_vals.update({'no_of_visits': args.get('goal_no_of_visits', 1)})
        if not args.get('goal_from_date', False):
            return False, api_global_function.return_failed_request_vals("Date Not provided",
                                                                         "عفوا التاريح مش موجود")
        if not args.get('goal_to_date', False):
            return False, api_global_function.return_failed_request_vals("TO Date Not provided",
                                                                         "عفوا التاريح الى مش موجود")
        visit_goal_vals.update({'date': args.get('goal_from_date', '')})
        visit_goal_vals.update({'to_date': args.get('goal_to_date', '')})

        return True, visit_goal_vals

    def add_new_goal(self, **args):
        request_id = args.get("goal_id", False)
        check_vals, visit_goal_vals = self.check_visit_goal_vals(args)
        if not check_vals:
            return visit_goal_vals
        try:
            if not request_id:
                visit_goal_obj = self.with_user(args.get('userId')).sudo().create(visit_goal_vals)
            else:
                # Update Request ID
                visit_goal_obj = self.with_user(args.get('userId')).sudo().browse(request_id)
                visit_goal_obj.with_user(args.get('userId')).sudo().write(visit_goal_vals)
        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        visit_goal_details = []
        for crmsalespersonplannervisitgoalsdetails_obj in visit_goal_obj.crmsalespersonplannervisitgoalsdetails_ids:
            visit_goal_details.append(
                {
                    'goal_line_id': crmsalespersonplannervisitgoalsdetails_obj.id,
                    'goal_line_name': crmsalespersonplannervisitgoalsdetails_obj.name or '',
                    'goal_line_partner_id': crmsalespersonplannervisitgoalsdetails_obj.partner_id.id or '',
                    'goal_line_partner_name': crmsalespersonplannervisitgoalsdetails_obj.partner_id.name or '',
                    'goal_line_partner_phone': crmsalespersonplannervisitgoalsdetails_obj.partner_phone or '',
                    'goal_line_partner_mobile': crmsalespersonplannervisitgoalsdetails_obj.partner_mobile or '',
                    'goal_line_date': crmsalespersonplannervisitgoalsdetails_obj.date or '',
                    'goal_line_user_id': crmsalespersonplannervisitgoalsdetails_obj.user_id.id,
                    'goal_line_user_name': crmsalespersonplannervisitgoalsdetails_obj.user_id.name,
                    'goal_line_description': crmsalespersonplannervisitgoalsdetails_obj.description or '',
                    'goal_line_state': self.get_state_name(crmsalespersonplannervisitgoalsdetails_obj.state) ,
                    'goal_line_visit_id': crmsalespersonplannervisitgoalsdetails_obj.visit_id.id,
                    'goal_line_visit_name': crmsalespersonplannervisitgoalsdetails_obj.visit_id.name or '',
                    'goal_line_goal_id': crmsalespersonplannervisitgoalsdetails_obj.goal_id.id or '',
                    'goal_line_goal_name': crmsalespersonplannervisitgoalsdetails_obj.goal_id.name or '',
                }
            )
        request_dic = {
            'goal_id': visit_goal_obj.id,
            'goal_name': visit_goal_obj.name or '',
            'goal_from_date': visit_goal_obj.date or '',
            'goal_to_date': visit_goal_obj.to_date or '',
            'goal_no_of_visits': visit_goal_obj.no_of_visits or '',
            'goal_user_id': visit_goal_obj.user_id.id,
            'goal_user_name': visit_goal_obj.user_id.name,
            'goal_details': visit_goal_details
        }
        if not request_id:
            ArabicMessage = "تم انشاء الطلب بنجاح رقم(%s)  " % str(visit_goal_obj.id)
            EnglishMessage = "Request Number (%s)has been created successfully." % str(visit_goal_obj.id)
        else:
            ArabicMessage = "تم تعديل الطلب بنجاح رقم(%s)  " % str(visit_goal_obj.id)
            EnglishMessage = "Request Number (%s)has been updated successfully." % str(visit_goal_obj.id)
        return {
            "Code": 200,
            "StatusDescription": "Success",
            "Data": request_dic,
            "ArabicMessage": ArabicMessage,
            "EnglishMessage": EnglishMessage
        }

    def do_action_create_goal_lines(self, **args):
        try:
            user_obj = self.env['res.users'].browse(args.get('userId'))
            if not args.get('goal_id', False):
                return False, api_global_function.return_failed_request_vals(
                    "Visit Goal ID is empty please check",
                    "عفوا هدف الزيارة غير موجود ")
            request_id = args.get("goal_id", False)
            visit_goal_obj = self.with_user(args.get('userId')).sudo().browse(request_id)
            visit_goal_obj.sudo().action_create_visits()
        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        visit_goal_details = []
        for crmsalespersonplannervisitgoalsdetails_obj in visit_goal_obj.crmsalespersonplannervisitgoalsdetails_ids:
            visit_goal_details.append(
                {
                    'goal_line_id': crmsalespersonplannervisitgoalsdetails_obj.id,
                    'goal_line_name': crmsalespersonplannervisitgoalsdetails_obj.name or '',
                    'goal_line_partner_id': crmsalespersonplannervisitgoalsdetails_obj.partner_id.id or '',
                    'goal_line_partner_name': crmsalespersonplannervisitgoalsdetails_obj.partner_id.name or '',
                    'goal_line_partner_phone': crmsalespersonplannervisitgoalsdetails_obj.partner_phone or '',
                    'goal_line_partner_mobile': crmsalespersonplannervisitgoalsdetails_obj.partner_mobile or '',
                    'goal_line_date': crmsalespersonplannervisitgoalsdetails_obj.date or '',
                    'goal_line_user_id': crmsalespersonplannervisitgoalsdetails_obj.user_id.id or '',
                    'goal_line_user_name': crmsalespersonplannervisitgoalsdetails_obj.user_id.name or '',
                    'goal_line_description': crmsalespersonplannervisitgoalsdetails_obj.description or '',
                    'goal_line_state': self.get_state_name(crmsalespersonplannervisitgoalsdetails_obj.state),
                    'goal_line_visit_id': crmsalespersonplannervisitgoalsdetails_obj.visit_id.id or '',
                    'goal_line_visit_name': crmsalespersonplannervisitgoalsdetails_obj.visit_id.name or '',
                    'goal_line_goal_id': crmsalespersonplannervisitgoalsdetails_obj.goal_id.id or '',
                    'goal_line_goal_name': crmsalespersonplannervisitgoalsdetails_obj.goal_id.name or '',
                }
            )
        request_dic = {
            'goal_id': visit_goal_obj.id or '',
            'goal_name': visit_goal_obj.name or '',
            'goal_from_date': visit_goal_obj.date or '',
            'goal_to_date': visit_goal_obj.to_date or '',
            'goal_no_of_visits': visit_goal_obj.no_of_visits or '',
            'goal_user_id': visit_goal_obj.user_id.id or '',
            'goal_user_name': visit_goal_obj.user_id.name or '',
            'goal_details': visit_goal_details
        }
        return {
            "Code": 200,
            "StatusDescription": "Success",
            "Data": request_dic,
            "ArabicMessage": "تم رجوع القائمه بنجاح",
            "EnglishMessage": "List Returned Successfully"
        }
        return api_global_function.return_success_update_api(visit_goal_obj.id, visit_goal_obj.id)

    def do_action_create_visits_as_goals(self, **args):
        try:
            user_obj = self.env['res.users'].browse(args.get('userId'))
            if not args.get('goal_id', False):
                return False, api_global_function.return_failed_request_vals(
                    "Visit Goal ID is empty please check",
                    "عفوا هدف الزيارة غير موجود ")
            request_id = args.get("goal_id", False)
            visit_goal_obj = self.with_user(args.get('userId')).sudo().browse(request_id)
            visit_goal_obj.sudo().action_create_visit_details()
        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        visit_goal_details = []
        for crmsalespersonplannervisitgoalsdetails_obj in visit_goal_obj.crmsalespersonplannervisitgoalsdetails_ids:
            visit_goal_details.append(
                {
                    'goal_line_id': crmsalespersonplannervisitgoalsdetails_obj.id,
                    'goal_line_name': crmsalespersonplannervisitgoalsdetails_obj.name or '',
                    'goal_line_partner_id': crmsalespersonplannervisitgoalsdetails_obj.partner_id.id or '',
                    'goal_line_partner_name': crmsalespersonplannervisitgoalsdetails_obj.partner_id.name or '',
                    'goal_line_partner_phone': crmsalespersonplannervisitgoalsdetails_obj.partner_phone or '',
                    'goal_line_partner_mobile': crmsalespersonplannervisitgoalsdetails_obj.partner_mobile or '',
                    'goal_line_date': crmsalespersonplannervisitgoalsdetails_obj.date or '',
                    'goal_line_user_id': crmsalespersonplannervisitgoalsdetails_obj.user_id.id or '',
                    'goal_line_user_name': crmsalespersonplannervisitgoalsdetails_obj.user_id.name or '',
                    'goal_line_description': crmsalespersonplannervisitgoalsdetails_obj.description or '',
                    'goal_line_state': self.get_state_name(crmsalespersonplannervisitgoalsdetails_obj.state),
                    'goal_line_visit_id': crmsalespersonplannervisitgoalsdetails_obj.visit_id.id or '',
                    'goal_line_visit_name': crmsalespersonplannervisitgoalsdetails_obj.visit_id.name or '',
                    'goal_line_goal_id': crmsalespersonplannervisitgoalsdetails_obj.goal_id.id or '',
                    'goal_line_goal_name': crmsalespersonplannervisitgoalsdetails_obj.goal_id.name or '',
                }
            )
        request_dic = {
            'goal_id': visit_goal_obj.id or '',
            'goal_name': visit_goal_obj.name or '',
            'goal_from_date': visit_goal_obj.date or '',
            'goal_to_date': visit_goal_obj.to_date or '',
            'goal_no_of_visits': visit_goal_obj.no_of_visits or '',
            'goal_user_id': visit_goal_obj.user_id.id or '',
            'goal_user_name': visit_goal_obj.user_id.name or '',
            'goal_details': visit_goal_details
        }
        return {
            "Code": 200,
            "StatusDescription": "Success",
            "Data": request_dic,
            "ArabicMessage": "تم رجوع القائمه بنجاح",
            "EnglishMessage": "List Returned Successfully"
        }
        return api_global_function.return_success_update_api(visit_goal_obj.id, visit_goal_obj.id)

class crm_salesperson_visits_goals_details(models.Model):
    _inherit = "crm.salesperson.planner.visit.goals.details"

    def update_goal_details(self, **args):
        try:
            visit_goal_details = []
            request_dic = {}
            user_obj = self.env['res.users'].browse(args.get('userId'))
            if not args.get('goal_details', []):
                return False, api_global_function.return_failed_request_vals(
                    "Visit Goal Detail List is empty please check",
                    "عفواتفاصيل  هدف الزيارة غير موجود ")
            for goal_detail in  args.get('goal_details', []):
                if not goal_detail.get('goal_line_id', False):
                    return False, api_global_function.return_failed_request_vals(
                        "Visit Goal Detail ID is empty please check",
                        "عفواتفاصيل  هدف الزيارة غير موجود ")
                request_id = goal_detail.get("goal_line_id", False)
                visit_goal_detail_obj = self.with_user(goal_detail.get('userId')).sudo().browse(request_id)
                if goal_detail.get('goal_line_date'):
                    visit_goal_detail_obj.sudo().date = goal_detail.get('goal_line_date')
                if goal_detail.get('goal_line_partner_id'):
                    if not self.env['res.partner'].sudo().search([('id', '=', int(goal_detail.get('goal_line_partner_id', False)))]):
                        return False, api_global_function.return_failed_request_vals("The Partner not exist profile",
                                                                                     "عفوا العميل غير موجود")
                    visit_goal_detail_obj.sudo().partner_id = int(goal_detail.get('goal_line_partner_id'))
                request_dic = {
                    'goal_id': visit_goal_detail_obj.goal_id.id or '',
                    'goal_name': visit_goal_detail_obj.goal_id.name or '',
                    'goal_from_date': visit_goal_detail_obj.goal_id.date or '',
                    'goal_to_date': visit_goal_detail_obj.goal_id.to_date or '',
                    'goal_no_of_visits': visit_goal_detail_obj.goal_id.no_of_visits or '',
                    'goal_user_id': visit_goal_detail_obj.goal_id.user_id.id or '',
                    'goal_user_name': visit_goal_detail_obj.goal_id.user_id.name or '',
                }
                visit_goal_details.append(
                    {
                        'goal_line_id': visit_goal_detail_obj.id,
                        'goal_line_name': visit_goal_detail_obj.name or '',
                        'goal_line_partner_id': visit_goal_detail_obj.partner_id.id or '',
                        'goal_line_partner_name': visit_goal_detail_obj.partner_id.name or '',
                        'goal_line_partner_phone': visit_goal_detail_obj.partner_phone or '',
                        'goal_line_partner_mobile': visit_goal_detail_obj.partner_mobile or '',
                        'goal_line_date': visit_goal_detail_obj.date or '',
                        'goal_line_user_id': visit_goal_detail_obj.user_id.id or '',
                        'goal_line_user_name': visit_goal_detail_obj.user_id.name or '',
                        'goal_line_description': visit_goal_detail_obj.description or '',
                        'goal_line_state': self.get_state_name(visit_goal_detail_obj.state),
                        'goal_line_visit_id': visit_goal_detail_obj.visit_id.id or '',
                        'goal_line_visit_name': visit_goal_detail_obj.visit_id.name or '',
                        'goal_line_goal_id': visit_goal_detail_obj.goal_id.id or '',
                        'goal_line_goal_name': visit_goal_detail_obj.goal_id.name or '',
                    }
                )
            if request_dic:
                request_dic.update({'goal_details': visit_goal_details})
        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        return {
            "Code": 200,
            "StatusDescription": "Success",
            "Data": request_dic,
            "ArabicMessage": "تم رجوع القائمه بنجاح",
            "EnglishMessage": "List Returned Successfully"
        }
        return api_global_function.return_success_update_api(visit_goal_detail_obj.id, visit_goal_detail_obj.id)

    def delete_goal_detail(self, **args):
        try:
            visit_goal_details = []
            request_dic = {}
            user_obj = self.env['res.users'].browse(args.get('userId'))
            if not args.get('goal_line_id', False):
                return False, api_global_function.return_failed_request_vals(
                    "Visit Goal Detail ID is empty please check",
                    "عفواتفاصيل  هدف الزيارة غير موجود ")
            request_id = args.get("goal_line_id", False)
            visit_goal_detail_obj = self.with_user(args.get('userId')).sudo().browse(request_id)
            if visit_goal_detail_obj.state in ['draft','', False]:
                visit_goal_detail_obj.sudo().unlink()
            else:
                return False, api_global_function.return_failed_request_vals(
                    "You can't delete visit goal detail as its not in draft state",
                    "عفوا لا يمكن مسح التفاصيل حيث انها غير مسودة  ")


        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        return api_global_function.return_success_delete_api(args.get('goal_line_id', False))

    def get_state_name(self, state_name):
        if state_name == 'draft':
            return 'Goal'
        elif state_name == 'confirm':
            return 'Checked In'
        elif state_name == 'done':
            return 'Visited'
        elif state_name == 'cancel':
            return 'Cancelled'
        elif state_name == 'incident':
            return 'Incident'
        else:
            return ''
