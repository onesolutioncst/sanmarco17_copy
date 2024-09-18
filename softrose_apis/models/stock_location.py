from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging
from odoo.tests import Form

from odoo.exceptions import ValidationError
from . import api_global_function

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class StockPicking(models.Model):
    _inherit = "stock.location"

    related_user_id = fields.Many2one('res.users','Related User')

    @api.model
    def get_all_destination_location(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_obj = self.env['res.users'].browse(args.get('userId'))
        distination_location = []
        try:
            stock_location_objs = self.env['stock.location'].sudo().search([])
            for stock_location_obj in stock_location_objs:
                distination_location.append(
                    {
                        'destination_location_id': stock_location_obj.id,
                        'destination_location_name': stock_location_obj.name,
                        'destination_location_display_name': stock_location_obj.display_name,
                    }
                )
        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        return {
            "Code": 200,
            "StatusDescription": "Success",
            "Data": distination_location,
            "ArabicMessage": "تم إسترجاع كميات الموجود بالمخازن بنجاح",
            "EnglishMessage": "Location Products Quantity have been Retrieved Successfully"
        }


