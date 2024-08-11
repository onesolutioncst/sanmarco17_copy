from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging
_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"
from . import api_global_function

class stock_quant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def get_my_qty_store(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_obj = self.env['res.users'].browse(args.get('userId'))
        stock_quant = []
        try:
            stock_quant_objs = self.env['stock.quant'].sudo().search([('location_id.related_user_id', '=', user_obj.id)])
            for stock_quant_obj in stock_quant_objs:
                stock_quant.append(
                    {
                        'stock_quant_id':  stock_quant_obj.id,
                        'product_id': stock_quant_obj.product_id.id,
                        'product_name': stock_quant_obj.product_id.name,
                        'quantity': stock_quant_obj.quantity,
                        'product_sale_price': stock_quant_obj.product_id.list_price,
                        'product_price_total': stock_quant_obj.product_id.list_price * stock_quant_obj.quantity
                    }
                )

        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        return {
            "Code": 200,
            "StatusDescription": "Success",
            "Data": stock_quant,
            "ArabicMessage": "تم إسترجاع كميات الموجود بالمخازن بنجاح",
            "EnglishMessage": "Location Products Quantity have been Retrieved Successfully"
        }