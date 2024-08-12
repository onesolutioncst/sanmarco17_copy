from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging
from . import api_global_function

_logger = logging.getLogger(__name__)


class res_country(models.Model):
    _inherit = "res.country"

    @api.model
    def get_all_countries(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        domain = []
        if 'country_id' in args and args.get('country_id'):
            if not self.env['res.country'].sudo().search([('id', '=', args.get('country_id'))]):
                return {
                    "Code": 500,
                    "StatusDescription": "Failed",
                    "Data": {},
                    "ArabicMessage": "رقم البلد غير صحيح",
                    "EnglishMessage": "Country ID is not Correct"
                }
            domain.append(('id', '=', args.get('country_id')))
        countries_objs = self.with_context(lang=lang).sudo().search(domain)
        result = []
        for country_obj in countries_objs:
            if country_obj.id == self.env.ref('base.sa').id:
                continue
            result.append({
                'country_id': country_obj.id,
                'country_name': country_obj.name,
                'country_code': country_obj.code
            })
        return api_global_function.return_success_list_api(result)


class res_country_state(models.Model):
    _inherit = "res.country.state"

    @api.model
    def get_all_states(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "`عفوا اللغه غير مدعومه")
        domain = []
        if 'state_id' in args and args.get('state_id'):
            if not self.env['res.country.state'].with_context(lang=lang).sudo().search(
                    [('id', '=', args.get('state_id'))]):
                return {
                    "Code": 500,
                    "StatusDescription": "Failed",
                    "Data": {},
                    "ArabicMessage": "رقم المدينه غير صحيح",
                    "EnglishMessage": "State ID is not Correct"
                }
            domain.append(('id', '=', args.get('state_id')))
        if 'country_id' in args and args.get('country_id'):
            if not self.env['res.country'].with_context(lang=lang).sudo().search([('id', '=', args.get('country_id'))]):
                return {
                    "Code": 500,
                    "StatusDescription": "Failed",
                    "Data": {},
                    "ArabicMessage": "رقم البلد غير صحيح",
                    "EnglishMessage": "Country ID is not Correct"
                }
            domain.append(('country_id', '=', args.get('country_id')))
        res_country_state_objs = self.with_context(lang=lang).sudo().search(domain)
        result = []
        for res_country_state_obj in res_country_state_objs:
            result.append({
                'state_id': res_country_state_obj.id,
                'state_name': res_country_state_obj.name,
                'state_code': res_country_state_obj.code
            })
        return api_global_function.return_success_list_api(result)
