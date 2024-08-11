from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

from odoo.exceptions import ValidationError
from . import api_global_function
_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"

class res_partner(models.Model):
    _inherit = "res.partner"

    client_location = fields.Char('Client location')
    crm_salesperson_planner_visit_ids = fields.One2many('crm.salesperson.planner.visit', 'partner_id', 'Visits')
    @api.model
    def get_all_clients(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        domain = []
        if args.get("client_id", False):
            domain.append(('id', '=', args.get("client_id", False)))
        res_partner_objs = self.env['res.partner'].sudo().with_context(lang=lang).search(domain)
        result = []
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for res_partner_obj in res_partner_objs:
            img_link = ''
            if res_partner_obj.image_1920:
                img_link = base_url + "/web/binary/download_document?model=res.partner&field=image_1920&id=" + str(res_partner_obj.id) + "&filename=image_1920.jpg"
            result.append({
                'client_id': res_partner_obj.id,
                'client_name': res_partner_obj.name or '',
                'client_phone': res_partner_obj.phone or '',
                'client_mobile': res_partner_obj.mobile or '',
                'client_email': res_partner_obj.email or '',
                'client_street': res_partner_obj.street or '',
                'client_street2': res_partner_obj.street2 or '',
                'client_city': res_partner_obj.city or '',
                'client_state_name': res_partner_obj.state_id.name or '',
                'client_zip': res_partner_obj.zip or '',
                'client_country_id': res_partner_obj.country_id.id or '',
                'client_country_name': res_partner_obj.country_id.name or '',
                "client_location": res_partner_obj.client_location,
                "client_lat": res_partner_obj.partner_latitude,
                "client_long": res_partner_obj.partner_longitude,
                "client_img": img_link
            })
        return api_global_function.return_success_list_api(result)

    def check_partner_vals(self, args):
        partner_vals = {'is_company': True,'customer_rank':1}
        if args.get("RequestID", False):
            partner_vals.update({'id': args.get("RequestID", False)})
        try:
            if not args.get('client_name', False):
                return False, api_global_function.return_failed_request_vals("Customer Name Not provided",
                                                                             "عفوا اسم العميل مش موجود")
            partner_vals.update({'name': args.get('client_name', False)})
            if not args.get('client_mobile', False):
                return False, api_global_function.return_failed_request_vals("Customer Mobile Not provided",
                                                                             "عفوا رقم الجوال مش موجود")
            partner_vals.update({'mobile': args.get('client_mobile', False)})
            if not args.get('client_email', False):
                return False, api_global_function.return_failed_request_vals("Customer Email Not provided",
                                                                             "عفوا البريد الالكترونى مش موجود")
            partner_vals.update({'email': args.get('client_email', False)})
            if args.get('client_phone', False):
                partner_vals.update({'phone': args.get('client_phone', False)})
            if args.get('client_street', False):
                partner_vals.update({'street': args.get('client_street', False)})
            if args.get('client_city', False):
                partner_vals.update({'city': args.get('client_city', False)})
            if args.get('client_zip', False):
                partner_vals.update({'zip': args.get('client_zip', False)})
            if args.get('client_location', False):
                partner_vals.update({'client_location': args.get('client_location', False)})
            if args.get('client_lat', False):
                partner_vals.update({'partner_latitude': args.get('client_lat', False)})
            if args.get('client_long', False):
                partner_vals.update({'partner_longitude': args.get('client_long', False)})
            if args.get('client_img', False):
                partner_vals.update({'image_1920': args.get('client_img', False)})
            if args.get('client_state_id', False):
                res_country_state_obj = self.env['res.country.state'].sudo().browse(int(args.get('client_state_id', False)))
                partner_vals.update({'state_id': args.get('client_state_id', False)})
            if args.get('client_country_id', False):
                res_country_obj = self.env['res.country'].sudo().browse(int(args.get('client_country_id', False)))
                partner_vals.update({'country_id': args.get('client_country_id', False)})
        except Exception as e:
            arabic_message = "%s  " % _(str(e)),
            englishmessage = "%s." % _(str(e))
            return False, api_global_function.return_failed_request_vals(englishmessage, arabic_message)
        return True, partner_vals

    def add_new_client(self, **args):
        #create new customer
        request_id = args.get("RequestID", False)
        check_vals, partner_vals = self.check_partner_vals(args)
        if not check_vals:
            return partner_vals
        try:
            if not request_id:
                res_partner_obj = self.with_user(args.get('userId')).sudo().create(partner_vals)
            else:
                #Update Request ID
                res_partner_obj = self.with_user(args.get('userId')).sudo().browse(request_id)
                res_partner_obj.with_user(args.get('userId')).sudo().write(partner_vals)
        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        if not request_id:
            return api_global_function.return_success_creation_api(res_partner_obj.id, res_partner_obj.id)
        else:
            return api_global_function.return_success_update_api(res_partner_obj.id, res_partner_obj.id)
