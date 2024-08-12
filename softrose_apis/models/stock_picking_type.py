from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging
_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"
from . import api_global_function

class stock_picking_type(models.Model):
    _inherit = "stock.picking.type"

    @api.model
    def get_all_user_operation_type(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_obj = self.env['res.users'].browse(args.get('userId'))
        stock_picking_type = []
        try:
            stock_picking_type_objs = self.env['stock.picking.type'].sudo().search(
                [('warehouse_id.lot_stock_id.related_user_id', '=', user_obj.id)])
            for stock_picking_type_obj in stock_picking_type_objs:
                stock_picking_type.append(
                    {
                        'operation_type_id': stock_picking_type_obj.id,
                        'operation_type_name': stock_picking_type_obj.name,
                        'operation_type_display_name': stock_picking_type_obj.display_name,
                        'operation_type_code': stock_picking_type_obj.code,
                    }
                )

        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        return {
            "Code": 200,
            "StatusDescription": "Success",
            "Data": stock_picking_type,
            "ArabicMessage": "تم إسترجاع نواع عمليات المخازن بنجاح",
            "EnglishMessage": "Operation Types have been Retrieved Successfully"
        }