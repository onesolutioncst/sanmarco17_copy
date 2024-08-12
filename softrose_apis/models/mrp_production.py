from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging
from odoo.tests import Form
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from . import api_global_function

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class mrp_production(models.Model):
    _inherit = "mrp.production"

    @api.model
    def get_all_delivery_and_return_orders(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_id = args.get('userId') and int(args.get('userId'))
        domain = [('user_id', '=', user_id)]
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        try:
            if args.get("product_id", False):
                product_product_obj = self.env['product.product'].sudo().search(
                    [('product_id', '=', int(args.get("product_id", False)))])
                if not product_product_obj:
                    return {
                        "Code": 500,
                        "StatusDescription": "Failed",
                        "Data": {},
                        "ArabicMessage": "رقم المنتج غير صحيح",
                        "EnglishMessage": "Product ID is not correct"
                    }
                domain.append(('product_id', '=', args.get("product_id", False)))
            if args.get("manufacture_id", False):
                mrp_production_obj = self.env['mrp.production'].sudo().search(
                    [('id', '=', int(args.get("manufacture_id", False)))])
                if not mrp_production_obj:
                    return {
                        "Code": 500,
                        "StatusDescription": "Failed",
                        "Data": {},
                        "ArabicMessage": "رقم امر التصتيع غير صحيح",
                        "EnglishMessage": "Manufacture ID is not correct"
                    }
                domain.append(('id', '=', args.get("manufacture_id", False)))
        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        mrp_production_list = []
        mrp_production_objs = self.env['mrp.production'].with_context(lang=lang).sudo().search(domain)
        for mrp_production_obj in mrp_production_objs:
            move_raw_list = []
            for move_raw_obj in mrp_production_obj.move_raw_ids:
                move_raw_list.append({
                    'id': move_raw_obj.id,
                    'product_id': move_raw_obj.product_id.id,
                    'product_name': move_raw_obj.product_id.name,
                    'to_consume': move_raw_obj.product_uom_qty,
                    'quantity': move_raw_obj.quantity,
                    'consumed': move_raw_obj.picked,
                })
            work_order_list=[]
            for workorder_obj in mrp_production_obj.workorder_ids:
                work_order_list.append({
                    'id': workorder_obj.id,
                    'operation': workorder_obj.name,
                    'workcenter_id': workorder_obj.workcenter_id.id,
                    'workcenter_name': workorder_obj.workcenter_id.name,
                    'product_id': workorder_obj.product_id.id,
                    'product_name': workorder_obj.product_id.name,
                    'quantity': workorder_obj.qty_remaining,
                    'expected_duration': '{0:02.0f}:{1:02.0f}'.format(*divmod(workorder_obj.duration_expected * 60, 60)),
                    'real_duration': '{0:02.0f}:{1:02.0f}'.format(*divmod(workorder_obj.duration * 60, 60)),
                    'status': dict(workorder_obj._fields['state'].selection).get(workorder_obj.state),
                    'start': workorder_obj.date_start,
                    'end': workorder_obj.date_finished,
                })
            mrp_production_list.append({
                'id': mrp_production_obj.id,
                'name': mrp_production_obj.name,
                'product_id': mrp_production_obj.product_id.id,
                'product_name': mrp_production_obj.product_id.name,
                'quantity': mrp_production_obj.product_qty,
                'unit_of_measure_id': mrp_production_obj.product_uom_id.id,
                'unit_of_measure_name': mrp_production_obj.product_uom_id.name,
                'start': mrp_production_obj.date_start,
                'end': mrp_production_obj.date_finished,
                'components_availability': mrp_production_obj.components_availability,
                'responsible_id':mrp_production_obj.user_id.id,
                'responsible_name':mrp_production_obj.user_id.name
            })
        return {
            "Code": 200,
            "StatusDescription": "Success",
            "Data": mrp_production_list,
            "ArabicMessage": "تم إسترجاع المعلومات بنجاح",
            "EnglishMessage": "Manufacture Orders have been Retrieved Successfully"
        }

    def check_manufacture_vals(self, args):
        manufacture_vals = {}
        if args.get("RequestID", False):
            manufacture_vals.update({'id': args.get("RequestID", False)})
        user_id = args.get('userId') and int(args.get('userId'))
        manufacture_vals.update({'user_id':user_id})
        manufacture_vals.update({'date_start': args.get('date_start', datetime.now()),
                                 'date_finished': args.get('date_finished', datetime.now() + timedelta(hours=1)),
                                 'product_qty': args.get('quantity', 1)})
        sale_order_line_list = []
        for component_line in args.get('component_line', []):
            component_line_dic = {}
            if not component_line.get('product_id', False):
                return False, api_global_function.return_failed_request_vals(
                    "Sales order lines product is empty please check",
                    "عفوا امر البيع خالى من المنتجات ")
            if not self.env['product.product'].sudo().search([('id', '=', component_line.get('product_id', False))]):
                return False, api_global_function.return_failed_request_vals("Product ID Not Correct",
                                                                             "عفوا المنتج غير صحيح")
            component_line_dic['product_id'] = component_line.get('product_id', False)
            component_line_dic['product_uom_qty'] = component_line.get('to_consume', 1)

    def add_new_manufacture_order(self, **args):
        request_id = args.get("RequestID", False)
        check_vals, manufacture_vals = self.check_manufacture_vals(args)
        if not check_vals:
            return manufacture_vals
        try:
            if not request_id:
                manufacture_order_obj = self.with_user(args.get('userId')).sudo().create(manufacture_vals)
            else:
                #Update Request ID
                manufacture_order_obj = self.with_user(args.get('userId')).sudo().browse(request_id)
                manufacture_order_obj.with_user(args.get('userId')).sudo().write(manufacture_vals)

        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        if not request_id:
            return api_global_function.return_success_creation_api(manufacture_order_obj.id, manufacture_order_obj.id)
        else:
            return api_global_function.return_success_update_api(manufacture_order_obj.id, manufacture_order_obj.id)