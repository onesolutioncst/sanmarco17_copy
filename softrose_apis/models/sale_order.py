from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

from odoo.exceptions import ValidationError
from . import api_global_function

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class sale_order(models.Model):
    _inherit = "sale.order"
    come_from = fields.Char('Come From')
    @api.model
    def get_sales_order_type(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_id = args.get('userId') and int(args.get('userId'))
        return api_global_function.return_success_list_api([{'default':'Default',
                                                            'governmental':'Governmental',
                                                            'cash':'Cash',
                                                            'sales_credit':'Sales Credit'}])
    @api.model
    def get_all_orders_client(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_id = args.get('userId') and int(args.get('userId'))
        domain = []
        if args.get("client_id", False):
            domain.append(('partner_id', '=', args.get("client_id", False)))
        if args.get("sales_order_id", False):
            domain.append(('id', '=', args.get("sales_order_id", False)))

        sale_order_objs = self.env['sale.order'].sudo().search(domain)
        result = []
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for sale_order_obj in sale_order_objs:
            project_count = self.env['project.project'].search_count([('sale_order_id', '=', sale_order_obj.id)])
            order_line_list = []
            for sale_order_line_obj in sale_order_obj.order_line:
                order_line_list.append({
                    'sale_line_id': sale_order_line_obj.id,
                    "product_id": sale_order_line_obj.product_id.id,
                    'product_name': sale_order_line_obj.product_id.name,
                    'product_img_link': base_url + "/web/binary/download_document?model=product.product&field=image_1920&id=" + str(sale_order_line_obj.product_id.id) + "&filename=image_1920.jpg",
                    "product_qty":sale_order_line_obj.product_uom_qty,
                    "product_qty_delivered":sale_order_line_obj.qty_delivered,
                    "product_qty_invoiced":sale_order_line_obj.qty_delivered,
                    'unit_of_measure_id': sale_order_line_obj.product_uom.id,
                    'unit_of_measure_name': sale_order_line_obj.product_uom.name,
                    "product_price":sale_order_line_obj.price_unit,
                    "product_discound":sale_order_line_obj.discount,
                    "product_price_subtotal":sale_order_line_obj.price_subtotal,
                    "product_price_total": sale_order_line_obj.price_total,

                })
            result.append({
                'client_id': sale_order_obj.partner_id.id,
                'client_name': sale_order_obj.partner_id.name,
                'sales_order_id': sale_order_obj.id,
                'sales_order_name': sale_order_obj.name or '',
                "sales_order_date": sale_order_obj.date_order or '',
                "sales_order_order_type": sale_order_obj.order_type,
                "sales_order_type": "Sales" if project_count == 0 else "Project",
                "sales_order_amount_untaxed": sale_order_obj.amount_untaxed,
                "sales_order_tax_amount": sale_order_obj.amount_tax,
                "sales_order_amount": sale_order_obj.amount_total,
                'sales_order_margin': sale_order_obj.margin,
                'sales_order_order_status': dict(sale_order_obj._fields['state'].selection).get(sale_order_obj.state),
                'sales_order_notes': sale_order_obj.note or '',
                "sales_order_details": order_line_list
            })
        return api_global_function.return_success_list_api(result)

    def check_saleorder_vals(self, args):
        sale_order_vals = {'pricelist_id':self.env.ref('product.list0').id}
        if args.get("RequestID", False):
            sale_order_vals.update({'id': args.get("RequestID", False)})
        try:
            if not args.get('partner_id', False):
                return False, api_global_function.return_failed_request_vals("Customer ID Not provided",
                                                                             "عفوا العميل مش موجود")
            if not self.env['res.partner'].sudo().search([('id','=',args.get('partner_id', False))]):
                return False, api_global_function.return_failed_request_vals("Customer ID Not Correct",
                                                                             "عفوا العميل غير صحيح")
            sale_order_vals.update({'partner_id': args.get("partner_id", False),'partner_invoice_id':args.get("partner_id", False),'partner_shipping_id':args.get("partner_id", False)})
            # if not args.get('come_from', False):
            #     return False, api_global_function.return_failed_request_vals("Come From Not provided",
            #                                                                  "عفوا المصدر مش موجود")
            sale_order_vals.update({'come_from': args.get('come_from', False)})
            sale_order_vals.update({'order_type': args.get('order_type', False)})

            if args.get('date_order', False):
                sale_order_vals.update({'date_order': args.get("date_order", False)})
            if not args.get('order_line', []):
                return False, api_global_function.return_failed_request_vals("Sales order lines is empty please check",
                                                                             "عفوا امر البيع خالى من المنتجات ")
            sale_order_line_dic={}
            sale_order_line_list = []
            for sale_order_line in args.get('order_line', []):
                sale_order_line_dic = {}
                if not sale_order_line.get('product_id', False):
                    return False, api_global_function.return_failed_request_vals(
                        "Sales order lines product is empty please check",
                        "عفوا امر البيع خالى من المنتجات ")
                if not self.env['product.product'].sudo().search([('id', '=', sale_order_line.get('product_id', False))]):
                    return False, api_global_function.return_failed_request_vals("Product ID Not Correct",
                                                                                 "عفوا المنتج غير صحيح")
                sale_order_line_dic['product_id'] = sale_order_line.get('product_id', False)
                # if self.env['product.product'].sudo().search([('id', '=', sale_order_line.get('product_id', False))]).percent_discount:
                #     sale_order_line_dic['discount'] = self.env['product.product'].sudo().search([('id', '=', sale_order_line.get('product_id', False))]).percent_discount
                if sale_order_line.get('discount', False):
                    sale_order_line_dic['discount'] = sale_order_line.get('discount', 0)
                if not sale_order_line.get('product_quantity', False):
                    return False, api_global_function.return_failed_request_vals(
                        "Sales order lines product Quantity is not provided",
                        "عفواالكميه الخاصه بالمنتج غير موجودة ")
                if sale_order_line.get('product_quantity', False) <= 0.0:
                    return False, api_global_function.return_failed_request_vals(
                        "Sales order lines product Quantity must be greater than Zero",
                        "عفواالكميه الخاصه بالمنتج لابد ان تكون اكبر من الزيرو ")
                sale_order_line_dic['product_uom_qty'] = sale_order_line.get('product_quantity', False)
                if not sale_order_line.get('unit_price', False):
                    return False, api_global_function.return_failed_request_vals(
                        "Sales order lines product price is not provided",
                        "عفوا سعر الخاص بالمنتج غير موجودة ")
                if sale_order_line.get('unit_price', False) <= 0.0:
                    return False, api_global_function.return_failed_request_vals(
                        "Sales order lines product price must be greater than Zero",
                        "عفوا السعر الخاص بالمنتج لابد ان تكون اكبر من الزيرو ")
                sale_order_line_dic['price_unit'] = sale_order_line.get('unit_price', False)
                sale_order_line_list.append((0, 0, sale_order_line_dic))
            sale_order_vals.update({'order_line': sale_order_line_list})
            sale_order_optionline_list = []
            for sale_order_option_line in args.get('optional_order_line', []):
                sale_order_option_line_dic = {}
                if not sale_order_option_line.get('product_id', False):
                    return False, api_global_function.return_failed_request_vals(
                        "Sales order lines product is empty please check",
                        "عفوا امر البيع خالى من المنتجات ")
                if not self.env['product.product'].sudo().search(
                        [('id', '=', sale_order_option_line.get('product_id', False))]):
                    return False, api_global_function.return_failed_request_vals("Product ID Not Correct",
                                                                                 "عفوا المنتج غير صحيح")
                sale_order_option_line_dic['product_id'] = sale_order_option_line.get('product_id', False)
                if not sale_order_option_line.get('product_quantity', False):
                    return False, api_global_function.return_failed_request_vals(
                        "Sales order lines product Quantity is not provided",
                        "عفواالكميه الخاصه بالمنتج غير موجودة ")
                if sale_order_option_line.get('product_quantity', False) <= 0.0:
                    return False, api_global_function.return_failed_request_vals(
                        "Sales order lines product Quantity must be greater than Zero",
                        "عفواالكميه الخاصه بالمنتج لابد ان تكون اكبر من الزيرو ")
                sale_order_option_line_dic['quantity'] = sale_order_option_line.get('product_quantity', False)
                if not sale_order_option_line.get('unit_price', False):
                    return False, api_global_function.return_failed_request_vals(
                        "Sales order lines product price is not provided",
                        "عفوا سعر الخاص بالمنتج غير موجودة ")
                if sale_order_option_line.get('unit_price', False) <= 0.0:
                    return False, api_global_function.return_failed_request_vals(
                        "Sales order lines product price must be greater than Zero",
                        "عفوا السعر الخاص بالمنتج لابد ان تكون اكبر من الزيرو ")
                sale_order_option_line_dic['price_unit'] = sale_order_option_line.get('unit_price', False)
                sale_order_optionline_list.append((0, 0, sale_order_option_line_dic))
            sale_order_vals.update({'sale_order_option_ids': sale_order_optionline_list})
        except Exception as e:
            arabic_message = "%s  " % _(str(e)),
            englishmessage = "%s." % _(str(e))
            return False, api_global_function.return_failed_request_vals(englishmessage, arabic_message)
        return True, sale_order_vals


    def add_new_orders_client(self, **args):
        request_id = args.get("RequestID", False)
        check_vals, sale_order_vals = self.check_saleorder_vals(args)
        if not check_vals:
            return sale_order_vals
        try:
            if not request_id:
                sale_order_obj = self.with_user(args.get('userId')).sudo().create(sale_order_vals)
                sale_order_obj.with_user(args.get('userId')).sudo().action_approval()
                sale_order_obj.with_user(args.get('userId')).sudo().action_confirm()
            else:
                #Update Request ID
                sale_order_obj = self.with_user(args.get('userId')).sudo().browse(request_id)
                sale_order_obj.with_user(args.get('userId')).sudo().write(sale_order_vals)

        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        if not request_id:
            return api_global_function.return_success_creation_api(sale_order_obj.id, sale_order_obj.id)
        else:
            return api_global_function.return_success_update_api(sale_order_obj.id, sale_order_obj.id)