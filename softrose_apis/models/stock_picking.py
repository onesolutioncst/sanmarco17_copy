from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging
from odoo.tests import Form
from datetime import datetime
from odoo.exceptions import ValidationError
from . import api_global_function

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class StockPicking(models.Model):
    _inherit = "stock.picking"

    return_picking_id = fields.Many2one('stock.picking')

    @api.model
    def get_all_delivery_and_return_orders(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        domain = []
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        try:
            if args.get("sales_order_id", False):
                sale_order_obj = self.env['sale.order'].sudo().search([('id','=',int(args.get("sales_order_id", False)))])
                if not sale_order_obj:
                    return {
                        "Code": 500,
                        "StatusDescription": "Failed",
                        "Data": {},
                        "ArabicMessage": "رقم امر البيع غير صحيح",
                        "EnglishMessage": "Sale order ID is not correct"
                    }
                domain.append(('sale_id', '=', args.get("sales_order_id", False)))

            else:
                return {
                    "Code": 500,
                    "StatusDescription": "Failed",
                    "Data": {},
                    "ArabicMessage": "رقم امر البيع غير موجود",
                    "EnglishMessage": "Sale order ID is not Provided"
                }

            if args.get("delivery_order_id", False):
                self.env['stock.picking'].sudo().browse(int(args.get("delivery_order_id", False)))
                picking_delivery_objs = self.env['stock.picking'].sudo().search(
                    domain + [('id', '=', args.get("delivery_order_id", False))])

            if args.get("return_order_id", False):
                self.env['stock.picking'].sudo().browse(int(args.get("delivery_order_id", False)))
                domain.append(('return_picking_id', '=', args.get("delivery_order_id", False)))
        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))

        for sale_order_ob in sale_order_obj:
            order_line_list = []
            for sale_order_line_obj in sale_order_ob.order_line:
                order_line_list.append({
                    'sale_line_id': sale_order_line_obj.id,
                    "product_id": sale_order_line_obj.product_id.id,
                    'product_name': sale_order_line_obj.product_id.name,
                    'product_img_link': base_url + "/web/binary/download_document?model=product.product&field=image_1920&id=" + str(
                        sale_order_line_obj.product_id.id) + "&filename=image_1920.jpg",
                    "product_qty": sale_order_line_obj.product_uom_qty,
                    "product_qty_delivered": sale_order_line_obj.qty_delivered,
                    "product_qty_invoiced": sale_order_line_obj.qty_delivered,
                    'unit_of_measure_id': sale_order_line_obj.product_uom.id,
                    'unit_of_measure_name': sale_order_line_obj.product_uom.name,
                    "product_price": sale_order_line_obj.price_unit,
                    "product_discound": sale_order_line_obj.discount,
                    "product_price_subtotal": sale_order_line_obj.price_subtotal,
                    "product_price_total": sale_order_line_obj.price_total,

                })

            if args.get("delivery_order_id", False):
                picking_objs = sale_order_ob.picking_ids.filtered(lambda rec: rec.id == int(args.get("delivery_order_id", False)))
                if not picking_objs:
                    return {
                        "Code": 500,
                        "StatusDescription": "Failed",
                        "Data": {},
                        "ArabicMessage": "رقم امر التسليم غير صحيح",
                        "EnglishMessage": "Delivery order ID is not Correct"
                    }
            else:
                picking_objs = sale_order_ob.picking_ids
            stock_picking_list = []
            for picking_obj in picking_objs.filtered(lambda rec: not rec.return_picking_id):
                stock_picking_line_list = []
                for stock_picking_line_obj in picking_obj.move_line_ids_without_package:
                    stock_picking_line_list.append(
                        {
                            'stock_picking_id': stock_picking_line_obj.id,
                            "product_id": stock_picking_line_obj.product_id.id,
                            'product_name': stock_picking_line_obj.product_id.name,
                            'product_img_link': base_url + "/web/binary/download_document?model=product.product&field=image_1920&id=" + str(
                                stock_picking_line_obj.product_id.id) + "&filename=image_1920.jpg",
                            "product_qty": stock_picking_line_obj.qty_done,
                            "reserved_product_qty": stock_picking_line_obj.reserved_uom_qty,
                            "product_uom_id": stock_picking_line_obj.product_uom_id.id,
                            "product_uom_name": stock_picking_line_obj.product_uom_id.name,
                        }
                    )
                # stock_picking_move_list = []
                # for stock_picking_move_obj in picking_obj.move_ids_without_package:
                #     stock_picking_move_list.append(
                #         {
                #             'stock_picking_id': stock_picking_move_obj.id,
                #             "product_id": stock_picking_move_obj.product_id.id,
                #             'product_name': stock_picking_move_obj.product_id.name,
                #             'product_img_link': base_url + "/web/binary/download_document?model=product.product&field=image_1920&id=" + str(
                #                 stock_picking_move_obj.product_id.id) + "&filename=image_1920.jpg",
                #             "product_qty": stock_picking_move_obj.quantity_done,
                #             "product_qty_delivered": stock_picking_move_obj.sale_line_id.qty_delivered,
                #             "product_qty_invoiced": stock_picking_move_obj.sale_line_id.qty_delivered,
                #
                #             "product_uom_id": stock_picking_move_obj.product_uom.id,
                #             "product_uom_name": stock_picking_move_obj.product_uom.name,
                #         }
                #     )
                if args.get("return_order_id", False):
                    return_picking_objs = self.env['stock.picking'].sudo().search([('return_picking_id','=',picking_obj.id),('id','=',int(args.get("return_order_id", False)))])
                    if not return_picking_objs:
                        return {
                            "Code": 500,
                            "StatusDescription": "Failed",
                            "Data": {},
                            "ArabicMessage": "رقم امر الاسترجاع غير صحيح",
                            "EnglishMessage": "Return Delivery order ID is not Correct"
                        }
                else:
                    return_picking_objs = self.env['stock.picking'].sudo().search([('return_picking_id', '=', picking_obj.id)])
                return_picking_list = []
                for return_picking_obj in return_picking_objs:
                    return_stock_picking_line_list = []
                    for return_stock_picking_line_obj in return_picking_obj.move_line_ids_without_package:
                        return_stock_picking_line_list.append(
                            {
                                'return_stock_line_picking_id': return_stock_picking_line_obj.id,
                                "product_id": return_stock_picking_line_obj.product_id.id,
                                'product_name': return_stock_picking_line_obj.product_id.name,
                                'product_img_link': base_url + "/web/binary/download_document?model=product.product&field=image_1920&id=" + str(
                                    return_stock_picking_line_obj.product_id.id) + "&filename=image_1920.jpg",
                                "product_qty": return_stock_picking_line_obj.qty_done,
                                "product_uom_id": return_stock_picking_line_obj.product_uom_id.id,
                                "product_uom_name": return_stock_picking_line_obj.product_uom_id.name,
                            }
                        )
                    return_stock_picking_move_list = []
                    for return_stock_picking_move_obj in return_picking_obj.move_ids_without_package:
                        return_stock_picking_move_list.append(
                            {
                                'return_stock_move_picking_id': return_stock_picking_move_obj.id,
                                "product_id": return_stock_picking_move_obj.product_id.id,
                                'product_name': return_stock_picking_move_obj.product_id.name,
                                'product_img_link': base_url + "/web/binary/download_document?model=product.product&field=image_1920&id=" + str(
                                    return_stock_picking_move_obj.product_id.id) + "&filename=image_1920.jpg",
                                "product_qty": return_stock_picking_move_obj.quantity_done,
                                "product_uom_id": return_stock_picking_move_obj.product_uom.id,
                                "product_uom_name": return_stock_picking_move_obj.product_uom.name,
                            }
                        )

                    return_picking_list.append({
                        "return_order_id ": return_picking_obj.id,
                        "return_order_name": return_picking_obj.name,
                        "return_order_date": return_picking_obj.scheduled_date if return_picking_obj.scheduled_date else '',
                        "return_order_notes": return_picking_obj.note if return_picking_obj.note else '',
                        "return_order_state":  dict(return_picking_obj._fields['state'].selection).get(return_picking_obj.state) ,
                        "return_order_operation": return_stock_picking_move_list,
                        "return_order_detail_operation": return_stock_picking_line_list,
                    })
                stock_picking_list.append({
                    "delivery_order_id ": picking_obj.id,
                    "delivery_order_name": picking_obj.name,
                    "delivery_order_date": picking_obj.scheduled_date if picking_obj.scheduled_date else '',
                    "delivery_order_notes": picking_obj.note if picking_obj.note else '',
                    "delivery_order_state": dict(picking_obj._fields['state'].selection).get(picking_obj.state),
                    # 'delivery_order_details': stock_picking_move_list,
                    "delivery_order_detail_operation": stock_picking_line_list,
                    "return_picking_list_count": len(return_picking_list),
                    "return_picking_list":return_picking_list
                })
            sale_order_data = {
                "sales_order_name": sale_order_obj.name,
                "sales_order_date": sale_order_obj.date_order,
                "sales_order_order_type": sale_order_obj.order_type,
                "sales_order_amount": sale_order_obj.amount_untaxed,
                "sales_order_tax_amount": sale_order_obj.amount_tax,
                "sales_order_total_amount": sale_order_obj.amount_total,
                "sales_order_notes": sale_order_obj.note or '',
                "sales_order_state": dict(sale_order_obj._fields['state'].selection).get(sale_order_obj.state),
                "sales_order_details": order_line_list,
                "sales_order_deliveries_count": len(stock_picking_list),
                "sales_order_deliveries": stock_picking_list
            }
        return {
            "Code": 200,
            "StatusDescription": "Success",
            "Data": sale_order_data,
            "ArabicMessage": "تم إسترجاع طلبات المرتجع للعميل بنجاح",
            "EnglishMessage": "Customer Return Orders have been Retrieved Successfully"
        }

    @api.model
    def add_new_return_orders(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_obj = self.env['res.users'].browse(args.get('userId'))
        domain = []
        try:
            if args.get("delivery_order_id", False):
                stock_picking_obj = self.env['stock.picking'].sudo().browse(int(args.get("delivery_order_id", False)))
                domain.append(('id', '=', args.get("delivery_order_id", False)))
                if not stock_picking_obj:
                    return {
                        "Code": 500,
                        "StatusDescription": "Failed",
                        "Data": {},
                        "ArabicMessage": "طلب التوصيل غير موجود",
                        "EnglishMessage": "Order is not found"
                    }
        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        user_location_id = self.env['stock.location'].sudo().search([('related_user_id', '=', user_obj.id)], limit=1)
        # if not user_location_id:
        #     return False, api_global_function.return_failed_request_vals(
        #         "Sorry no location assigned for this user ",
        #         "عفوا لا يوجد مخزن لهذا المستخدم المندوب ")
        wizard_form = Form(
            self.env['stock.return.picking'].with_user(user_obj.id).with_company(
                user_obj.company_id.id).sudo().with_context(active_id=args.get('delivery_order_id', False),
                                                            active_model='stock.picking'))

        wizard = wizard_form.save()
        for return_order_line in args.get('return_order_lines', []):
            if not return_order_line.get('product_id', False):
                return False, api_global_function.return_failed_request_vals(
                    "Return order lines product is empty please check",
                    "عفوا امر الارجاع خالى من المنتجات ")
            if not self.env['product.product'].sudo().search(
                    [('id', '=', return_order_line.get('product_id', False))]):
                return False, api_global_function.return_failed_request_vals("Product ID Not Correct",
                                                                             "عفوا المنتج غير صحيح")
            if not return_order_line.get('return_quantity', False):
                return False, api_global_function.return_failed_request_vals(
                    "Return order lines product Done Quantity is not provided",
                    "عفواالكميه الخاصه بالمنتج غير موجودة ")
            if return_order_line.get('return_quantity', False) <= 0.0:
                return False, api_global_function.return_failed_request_vals(
                    "Return order lines product Quantity must be greater than Zero",
                    "عفواالكميه الخاصه بالمنتج لابد ان تكون اكبر من الزيرو ")
            product_return_move = wizard.product_return_moves.filtered(lambda rec: rec.product_id.id==return_order_line.get('product_id', False))
            if not product_return_move:
                return False, api_global_function.return_failed_request_vals(
                    "Return order lines product doesn't exist",
                    "عفوا المنتج غير موجود للارجاع ")
            product_return_move.quantity=return_order_line.get('return_quantity', False)
        stock_return_picking_action = wizard.with_user(user_obj.id).with_company(user_obj.company_id.id).sudo().create_returns()
        return_pick = self.env['stock.picking'].browse(stock_return_picking_action['res_id'])
        immediate_trans_wiz_dict = return_pick.sudo().with_user(user_obj.id).button_validate()
        immediate_trans_wiz = Form(self.sudo().env[immediate_trans_wiz_dict['res_model']].with_context(immediate_trans_wiz_dict['context'])).save()
        immediate_trans_wiz.with_user(SUPERUSER_ID).sudo().process()
        # immediate_trans_wiz.with_user(user_obj.id).sudo().process()  #odoobot to create backorder
        for return_order_line in args.get('return_order_lines', []):
            return_pick.move_ids.filtered(lambda rec: rec.product_id.id==return_order_line.get('product_id', False)).sudo().quantity_done = return_order_line.get('return_quantity', False)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        stock_picking_return_data = {
            "return_order_id ": return_pick.id,
            "return_order_name": return_pick.name,
            "return_order_date": return_pick.scheduled_date if return_pick.scheduled_date else '',
            "return_order_notes ": return_pick.note if return_pick.note else '',
        }
        stock_picking_return_line_list = []
        for stock_picking_line_obj in return_pick.move_ids_without_package:
            stock_picking_return_line_list.append({
                # 'stock_picking_id': stock_picking_line_obj.id,
                "product_id": stock_picking_line_obj.product_id.id,
                'product_name': stock_picking_line_obj.product_id.name,
                'product_img_link': base_url + "/web/binary/download_document?model=product.product&field=image_1920&id=" + str(
                    stock_picking_line_obj.product_id.id) + "&filename=image_1920.jpg",
                "product_qty": stock_picking_line_obj.quantity_done,
                "product_uom_id": stock_picking_line_obj.product_uom.id,
                "product_uom_name": stock_picking_line_obj.product_uom.name,
            })
        stock_picking_return_data.update(
            {
                'return_order_details': stock_picking_return_line_list
            }
        )
        return {
            "Code": 200,
            "StatusDescription": "Success",
            "Data": stock_picking_return_data,
            "ArabicMessage": "تم اضافة  طلبات مرتجع  للعميل بنجاح",
            "EnglishMessage": "Customer Return Orders has been Added Successfully"
        }

    @api.model
    def add_new_user_transfer(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_obj = self.env['res.users'].browse(args.get('userId'))
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        stock_picking_dic = {}
        if args.get("operation_type_id", False):
            stock_picking_type_obj = self.env['stock.picking.type'].sudo().browse(int(args.get("operation_type_id", False)))
            if not stock_picking_type_obj:
                return {
                    "Code": 500,
                    "StatusDescription": "Failed",
                    "Data": {},
                    "ArabicMessage": "نوع العملية غير موجود",
                    "EnglishMessage": "Operation type ID is not found"
                }
            stock_picking_dic['picking_type_id'] = stock_picking_type_obj.id
        else:
            return {
                "Code": 500,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "رقم نوع العملية غير صحيح",
                "EnglishMessage": "Operation type ID is not Correct"
            }
        if args.get("destination_location_id", False):
            destination_location_obj = self.env['stock.location'].sudo().browse(
                int(args.get("destination_location_id", False)))
            if not destination_location_obj:
                return {
                    "Code": 500,
                    "StatusDescription": "Failed",
                    "Data": {},
                    "ArabicMessage": "المخزن النهائى غير موجود",
                    "EnglishMessage": "Destination Locaton ID is not found"
                }
            stock_picking_dic['location_dest_id'] = destination_location_obj.id
        else:
            return {
                "Code": 500,
                "StatusDescription": "Failed",
                "Data": {},
                "ArabicMessage": "رقم المخزن النهائى غير صحيح",
                "EnglishMessage": "Destination Locaton ID is not Correct"
            }
        if args.get("partner_id", False):
            res_partner_obj = self.env['res.partner'].sudo().browse(
                int(args.get("partner_id", False)))
            if not res_partner_obj:
                return {
                    "Code": 500,
                    "StatusDescription": "Failed",
                    "Data": {},
                    "ArabicMessage": "العميل غير موجود",
                    "EnglishMessage": "Partner ID is not found"
                }
            stock_picking_dic['partner_id'] = res_partner_obj.id
        stock_picking_dic['note'] = args.get("transfer_order_notes", '')
        stock_picking_dic['user_id'] = user_obj.id
        user_obj
        stock_picking_dic['scheduled_date'] = datetime.now()
        # if user_obj.property_warehouse_id and user_obj.property_warehouse_id.lot_stock_id:
        #     user_warehouse_location_obj = user_obj.property_warehouse_id.lot_stock_id
        # else:
        #     return {
        #         "Code": 500,
        #         "StatusDescription": "Failed",
        #         "Data": {},
        #         "ArabicMessage": "عفوا لا يوجد مخزن للمستخدم (المندوب)",
        #         "EnglishMessage": "Theres no default warehouse on salesperson user"
        #     }

        order_lines = args.get('transfer_order_lines', [])
        stock_picking_line_list = []
        for order_line_data in order_lines:
            if order_line_data.get("product_id", False):
                product_obj = self.env['product.product'].sudo().browse(
                    int(order_line_data.get("product_id", False)))
                if not product_obj:
                    return {
                        "Code": 500,
                        "StatusDescription": "Failed",
                        "Data": {},
                        "ArabicMessage": "المنتج غير موجود",
                        "EnglishMessage": "Product ID is not found"
                    }
            else:
                return {
                    "Code": 500,
                    "StatusDescription": "Failed",
                    "Data": {},
                    "ArabicMessage": "رقم المنتج غير صحيح",
                    "EnglishMessage": "Product ID is not Correct"
                }
            customer_loc = stock_picking_type_obj.default_location_src_id
            if not stock_picking_type_obj.default_location_src_id:
                customer_loc, supplier_loc = self.env['stock.warehouse'].sudo()._get_partner_locations()
            stock_picking_line_list.append((0, 0, {
                'picking_type_id': stock_picking_type_obj.id,
                'location_id': customer_loc.id,
                'location_dest_id': destination_location_obj.id,
                'company_id': user_obj.company_id.id,
                'name': product_obj.name,
                'product_id': product_obj.id,
                'product_uom_qty': order_line_data.get('product_uom_qty', 0.0),
                # 'quantity_done': order_line_data.get('product_quantity', 0.0),
            }))
        stock_picking_dic.update({'move_ids': stock_picking_line_list})
        stock_picking_obj = self.env['stock.picking'].sudo().create(stock_picking_dic)

        # stock_picking_obj.action_confirm()
        # stock_picking_obj.action_set_quantities_to_reservation()
        # stock_picking_obj.with_user(user_obj.id).button_validate()
        stock_picking_line_list = []
        for stock_picking_line_obj in stock_picking_obj.move_line_ids_without_package:
            stock_picking_line_list.append({
                'stock_picking_id': stock_picking_line_obj.id,
                "product_id": stock_picking_line_obj.product_id.id,
                'product_name': stock_picking_line_obj.product_id.name,
                'product_img_link': base_url + "/web/binary/download_document?model=product.product&field=image_1920&id=" + str(
                    stock_picking_line_obj.product_id.id) + "&filename=image_1920.jpg",
                "product_qty_done": stock_picking_line_obj.qty_done,
                "product_qty_demand": stock_picking_line_obj.product_uom_qty,
                "reserved_product_qty": stock_picking_line_obj.reserved_uom_qty,
                "product_uom_id": stock_picking_line_obj.product_uom_id.id,
                "product_uom_name": stock_picking_line_obj.product_uom_id.name,
            })
        stock_picking_move_list = []
        for stock_picking_move_obj in stock_picking_obj.move_ids_without_package:
            stock_picking_move_list.append(
                {
                    'stock_picking_id': stock_picking_move_obj.id,
                    "product_id": stock_picking_move_obj.product_id.id,
                    'product_name': stock_picking_move_obj.product_id.name,
                    'product_img_link': base_url + "/web/binary/download_document?model=product.product&field=image_1920&id=" + str(
                        stock_picking_move_obj.product_id.id) + "&filename=image_1920.jpg",

                    "product_qty_demand": stock_picking_move_obj.product_uom_qty,
                    "product_qty_done": stock_picking_move_obj.quantity_done,
                    "product_uom_id": stock_picking_move_obj.product_uom.id,
                    "product_uom_name": stock_picking_move_obj.product_uom.name,
                }
            )
        stock_picking_return_data = {
            "transfer_order_id": stock_picking_obj.id,
            "transfer_order_name": stock_picking_obj.name,
            "transfer_order_date": stock_picking_obj.scheduled_date if stock_picking_obj.scheduled_date else '',
            "transfer_order_notes ": stock_picking_obj.note if stock_picking_obj.note else '',
            "transfer_order_state": dict(stock_picking_obj._fields['state'].selection).get(stock_picking_obj.state),
            'transfer_order_details': stock_picking_move_list,
            "transfer_order_detail_operation": stock_picking_line_list,
        }

        return {
            "Code": 200,
            "StatusDescription": "Success",
            "Data": stock_picking_return_data,
            "ArabicMessage": "تم اضافة  طلبات توصيل  للعميل بنجاح",
            "EnglishMessage": "Customer Delivery Orders has been Added Successfully"
        }

    @api.model
    def update_delivery_order(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_obj = self.env['res.users'].browse(args.get('userId'))
        try:
            if args.get("delivery_order_id", False):
                stock_picking_obj = self.env['stock.picking'].sudo().search([('id','=',int(args.get("delivery_order_id", False)))])
                if not stock_picking_obj:
                    return {
                        "Code": 500,
                        "StatusDescription": "Failed",
                        "Data": {},
                        "ArabicMessage": "رقم امر التوريد غير صحيح",
                        "EnglishMessage": "Delivery order ID is not correct"
                    }
            else:
                return {
                    "Code": 500,
                    "StatusDescription": "Failed",
                    "Data": {},
                    "ArabicMessage": "رقم امر التوريد غير موجود",
                    "EnglishMessage": "Delivery order ID is not Provided"
                }
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            # if user_obj.sudo().property_warehouse_id and user_obj.sudo().property_warehouse_id.lot_stock_id:
            user_location_id = self.env['stock.location'].sudo().search([('related_user_id','=',user_obj.id)], limit=1)
            # if user_location_id:
            #     stock_picking_obj.sudo().location_id  = user_location_id.id
            for delivery_order_line in args.get('delivery_order_lines', []):
                if not delivery_order_line.get('stock_picking_id', False):
                    return False, api_global_function.return_failed_request_vals(
                        "Delivery order lines ID is empty please check",
                        "عفوا امر التوريد خالى من اوامر التوريد ")
                if not self.env['stock.move.line'].sudo().search(
                        [('id', '=', delivery_order_line.get('stock_picking_id', False))]):
                    return False, api_global_function.return_failed_request_vals("Delivery Order line ID Not Correct",
                                                                                 "عفوا امر التوريد غير صحيح")
                stock_move_line_obj = self.env['stock.move.line'].sudo().search(
                    [('id', '=', delivery_order_line.get('stock_picking_id', False))])
                if not delivery_order_line.get('product_id', False):
                    return False, api_global_function.return_failed_request_vals(
                        "Delivery order lines product is empty please check",
                        "عفوا امر التوريد خالى من المنتجات ")
                if not self.env['product.product'].sudo().search([('id', '=', delivery_order_line.get('product_id', False))]):
                    return False, api_global_function.return_failed_request_vals("Product ID Not Correct",
                                                                                 "عفوا المنتج غير صحيح")
                # if not delivery_order_line.get('product_done_quantity', False):
                #     return False, api_global_function.return_failed_request_vals(
                #         "Delivery order lines product Done Quantity is not provided",
                #         "عفواالكميه الخاصه بالمنتج غير موجودة ")
                if delivery_order_line.get('product_done_quantity', False) < 0.0:
                    return False, api_global_function.return_failed_request_vals(
                        "Delivery order lines product Quantity must be greater than Zero",
                        "عفواالكميه الخاصه بالمنتج لابد ان تكون اكبر من الزيرو ")

                stock_move_line_dict = {'qty_done': delivery_order_line.get('product_done_quantity', False)}
                # if user_location_id:
                #     stock_move_line_dict.update({'location_id': user_location_id.id})
                stock_move_line_obj.with_user(args.get('userId')).sudo().write(stock_move_line_dict)
            action = stock_picking_obj.with_user(args.get('userId')).sudo().button_validate()
            picking_context = dict(self.env.context, default_show_transfers=True,
                            default_pick_ids=[(4, p.id) for p in stock_picking_obj])
            try:
                backorder_wizard = Form(self.env['stock.backorder.confirmation'].sudo().with_context(action['context'])).save()
            except Exception as e:
                backorder_wizard = Form(
                    self.env['stock.backorder.confirmation'].sudo().with_context(picking_context)).save()
            backorder_wizard.with_user(args.get('userId')).sudo().process()
            stock_picking_line_list = []
            for stock_picking_line_obj in stock_picking_obj.move_line_ids_without_package:
                stock_picking_line_list.append({
                    'stock_picking_id': stock_picking_line_obj.id,
                    "product_id": stock_picking_line_obj.product_id.id,
                    'product_name': stock_picking_line_obj.product_id.name,
                    'product_img_link': base_url + "/web/binary/download_document?model=product.product&field=image_1920&id=" + str(
                        stock_picking_line_obj.product_id.id) + "&filename=image_1920.jpg",
                    "product_qty": stock_picking_line_obj.qty_done,
                    "reserved_product_qty": stock_picking_line_obj.reserved_uom_qty,
                    "product_uom_id": stock_picking_line_obj.product_uom_id.id,
                    "product_uom_name": stock_picking_line_obj.product_uom_id.name,
                })
            stock_picking_dic = {
                "delivery_order_id ": stock_picking_obj.id,
                "delivery_order_name": stock_picking_obj.name,
                "delivery_order_date": stock_picking_obj.scheduled_date if stock_picking_obj.scheduled_date else '',
                "delivery_order_notes": stock_picking_obj.note if stock_picking_obj.note else '',
                "delivery_order_state": dict(stock_picking_obj._fields['state'].selection).get(stock_picking_obj.state),
                "sales_order_deliveries_count": len(stock_picking_obj),
                # 'delivery_order_details': stock_picking_move_list,
                "delivery_order_detail_operation": stock_picking_line_list,

            }
        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        return api_global_function.return_success_list_api([stock_picking_dic])

    @api.model
    def update_user_transfer(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_obj = self.env['res.users'].browse(args.get('userId'))
        try:
            stock_picking_dic = {}
            if args.get("operation_type_id", False):
                stock_picking_type_obj = self.env['stock.picking.type'].sudo().browse(
                    int(args.get("operation_type_id", False)))
                if not stock_picking_type_obj:
                    return {
                        "Code": 500,
                        "StatusDescription": "Failed",
                        "Data": {},
                        "ArabicMessage": "نوع العملية غير موجود",
                        "EnglishMessage": "Operation type ID is not found"
                    }
                stock_picking_dic['picking_type_id'] = stock_picking_type_obj.id
            if args.get("destination_location_id", False):
                destination_location_obj = self.env['stock.location'].sudo().browse(
                    int(args.get("destination_location_id", False)))
                if not destination_location_obj:
                    return {
                        "Code": 500,
                        "StatusDescription": "Failed",
                        "Data": {},
                        "ArabicMessage": "المخزن النهائى غير موجود",
                        "EnglishMessage": "Destination Locaton ID is not found"
                    }
                stock_picking_dic['location_dest_id'] = destination_location_obj.id
            if args.get("transfer_order_notes", False):
                stock_picking_dic['note'] = args.get("transfer_order_notes", '')
            if args.get("transfer_order_id", False):
                stock_picking_obj = self.env['stock.picking'].sudo().search(
                    [('id', '=', int(args.get("transfer_order_id", False)))])
                if not stock_picking_obj:
                    return {
                        "Code": 500,
                        "StatusDescription": "Failed",
                        "Data": {},
                        "ArabicMessage": "رقم امر التوريد غير صحيح",
                        "EnglishMessage": "Delivery order ID is not correct"
                    }
                if stock_picking_dic:
                    stock_picking_obj.with_user(args.get('userId')).sudo().write(stock_picking_dic)
            else:
                return {
                    "Code": 500,
                    "StatusDescription": "Failed",
                    "Data": {},
                    "ArabicMessage": "رقم امر التوريد غير موجود",
                    "EnglishMessage": "Delivery order ID is not Provided"
                }
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            # if user_obj.sudo().property_warehouse_id and user_obj.sudo().property_warehouse_id.lot_stock_id:
            user_location_id = self.env['stock.location'].sudo().search([('related_user_id', '=', user_obj.id)],
                                                                        limit=1)
            # if user_location_id:
            #     stock_picking_obj.sudo().location_id  = user_location_id.id
            for delivery_order_line in args.get('transfer_order_lines', []):
                if not delivery_order_line.get('stock_picking_id', False):
                    return False, api_global_function.return_failed_request_vals(
                        "Delivery order lines ID is empty please check",
                        "عفوا امر التوريد خالى من اوامر التوريد ")
                if not self.env['stock.move'].sudo().search(
                        [('id', '=', delivery_order_line.get('stock_picking_id', False))]):
                    return False, api_global_function.return_failed_request_vals("Delivery Order line ID Not Correct",
                                                                                 "عفوا امر التوريد غير صحيح")
                stock_move_line_obj = self.env['stock.move'].sudo().search(
                    [('id', '=', delivery_order_line.get('stock_picking_id', False))])
                if not delivery_order_line.get('product_id', False):
                    return False, api_global_function.return_failed_request_vals(
                        "Delivery order lines product is empty please check",
                        "عفوا امر التوريد خالى من المنتجات ")
                if not self.env['product.product'].sudo().search(
                        [('id', '=', delivery_order_line.get('product_id', False))]):
                    return False, api_global_function.return_failed_request_vals("Product ID Not Correct",
                                                                                 "عفوا المنتج غير صحيح")
                # if not delivery_order_line.get('product_done_quantity', False):
                #     return False, api_global_function.return_failed_request_vals(
                #         "Delivery order lines product Done Quantity is not provided",
                #         "عفواالكميه الخاصه بالمنتج غير موجودة ")
                if delivery_order_line.get('product_done_quantity', False) < 0.0:
                    return False, api_global_function.return_failed_request_vals(
                        "Delivery order lines product Quantity must be greater than Zero",
                        "عفواالكميه الخاصه بالمنتج لابد ان تكون اكبر من الزيرو ")

                stock_move_line_dict = {'product_uom_qty': delivery_order_line.get('product_done_quantity', False)}
                # if user_location_id:
                #     stock_move_line_dict.update({'location_id': user_location_id.id})
                stock_move_line_obj.with_user(args.get('userId')).sudo().write(stock_move_line_dict)
            # action = stock_picking_obj.with_user(args.get('userId')).sudo().button_validate()
            # picking_context = dict(self.env.context, default_show_transfers=True,
            #                        default_pick_ids=[(4, p.id) for p in stock_picking_obj])
            # try:
            #     backorder_wizard = Form(
            #         self.env['stock.backorder.confirmation'].sudo().with_context(action['context'])).save()
            # except Exception as e:
            #     backorder_wizard = Form(
            #         self.env['stock.backorder.confirmation'].sudo().with_context(picking_context)).save()
            # backorder_wizard.with_user(args.get('userId')).sudo().process()
            stock_picking_move_list = []
            for stock_picking_move_obj in stock_picking_obj.move_ids_without_package:
                stock_picking_move_list.append(
                    {
                        'stock_picking_id': stock_picking_move_obj.id,
                        "product_id": stock_picking_move_obj.product_id.id,
                        'product_name': stock_picking_move_obj.product_id.name,
                        'product_img_link': base_url + "/web/binary/download_document?model=product.product&field=image_1920&id=" + str(
                            stock_picking_move_obj.product_id.id) + "&filename=image_1920.jpg",

                        "product_qty_demand": stock_picking_move_obj.product_uom_qty,
                        "product_qty_done": stock_picking_move_obj.quantity_done,
                        "product_uom_id": stock_picking_move_obj.product_uom.id,
                        "product_uom_name": stock_picking_move_obj.product_uom.name,
                    }
                )
            stock_picking_line_list = []
            for stock_picking_line_obj in stock_picking_obj.move_line_ids_without_package:
                stock_picking_line_list.append({
                    'stock_picking_id': stock_picking_line_obj.id,
                    "product_id": stock_picking_line_obj.product_id.id,
                    'product_name': stock_picking_line_obj.product_id.name,
                    'product_img_link': base_url + "/web/binary/download_document?model=product.product&field=image_1920&id=" + str(
                        stock_picking_line_obj.product_id.id) + "&filename=image_1920.jpg",
                    "product_qty": stock_picking_line_obj.qty_done,
                    "reserved_product_qty": stock_picking_line_obj.reserved_uom_qty,
                    "product_uom_id": stock_picking_line_obj.product_uom_id.id,
                    "product_uom_name": stock_picking_line_obj.product_uom_id.name,
                })
            stock_picking_dic = {
                "transfer_order_id": stock_picking_obj.id,
                "transfer_order_name": stock_picking_obj.name,
                "transfer_order_date": stock_picking_obj.scheduled_date if stock_picking_obj.scheduled_date else '',
                "transfer_order_notes": stock_picking_obj.note if stock_picking_obj.note else '',
                "transfer_order_state": dict(stock_picking_obj._fields['state'].selection).get(stock_picking_obj.state),
                # "sales_order_deliveries_count": len(stock_picking_obj),
                'transfer_order_details': stock_picking_move_list,
                "transfer_order_detail_operation": stock_picking_line_list,

            }
        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        return api_global_function.return_success_list_api([stock_picking_dic])

    @api.model
    def get_all_user_transfer(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_obj = self.env['res.users'].browse(args.get('userId'))
        domain = []
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        try:
            if args.get("transfer_order_id", False):
                self.env['stock.picking'].sudo().browse(int(args.get("transfer_order_id", False)))
                domain.append(('id', '=', args.get("transfer_order_id", False)))
            if args.get("transfer_operation_type_id", False):
                self.env['stock.picking.type'].sudo().browse(int(args.get("transfer_operation_type_id", False)))
                domain.append(('picking_type_id', '=', args.get("transfer_operation_type_id", False)))
            if args.get("user_type", False):
                if args.get("user_type", False) not in ['responsible', 'source_responsible', 'dest_responsible']:
                    return api_global_function.return_failed_request_vals("Wrong User type", "عفوا نوع اليوزر غير صحيح")
                if args.get("user_type", False) == 'responsible':
                    domain.append(('user_id','=',user_obj.id))
                elif args.get("user_type", False) == 'source_responsible':
                    domain.append(('location_id.related_user_id','=',user_obj.id))
                elif args.get("user_type", False) == 'dest_responsible':
                    domain.append(('location_dest_id.related_user_id','=',user_obj.id))
            else:
                return api_global_function.return_failed_request_vals("User type not exist", "عفوا نوع اليوزر غير موجود")
        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        picking_delivery_objs = self.env['stock.picking'].sudo().search(domain, order = 'id desc')
        stock_picking_list = []
        for picking_obj in picking_delivery_objs: #.filtered(lambda rec: not rec.return_picking_id):
            stock_picking_line_list = []
            for stock_picking_line_obj in picking_obj.move_line_ids_without_package:
                stock_picking_line_list.append(
                    {
                        'stock_picking_id': stock_picking_line_obj.id,
                        "product_id": stock_picking_line_obj.product_id.id,
                        'product_name': stock_picking_line_obj.product_id.name,
                        'product_img_link': base_url + "/web/binary/download_document?model=product.product&field=image_1920&id=" + str(
                            stock_picking_line_obj.product_id.id) + "&filename=image_1920.jpg",
                        "product_qty": stock_picking_line_obj.qty_done,
                        "reserved_product_qty": stock_picking_line_obj.reserved_uom_qty,
                        "product_uom_id": stock_picking_line_obj.product_uom_id.id,
                        "product_uom_name": stock_picking_line_obj.product_uom_id.name,
                    }
                )
            stock_picking_move_list = []
            for stock_picking_move_obj in picking_obj.move_ids_without_package:
                stock_picking_move_list.append(
                    {
                        'stock_picking_id': stock_picking_move_obj.id,
                        "product_id": stock_picking_move_obj.product_id.id,
                        'product_name': stock_picking_move_obj.product_id.name,
                        'product_img_link': base_url + "/web/binary/download_document?model=product.product&field=image_1920&id=" + str(
                            stock_picking_move_obj.product_id.id) + "&filename=image_1920.jpg",
                        "product_qty": stock_picking_move_obj.quantity_done,
                        "product_uom_qty": stock_picking_move_obj.product_uom_qty,
                        "product_qty_delivered": stock_picking_move_obj.sale_line_id.qty_delivered,
                        "product_qty_invoiced": stock_picking_move_obj.sale_line_id.qty_delivered,

                        "product_uom_id": stock_picking_move_obj.product_uom.id,
                        "product_uom_name": stock_picking_move_obj.product_uom.name,
                    }
                )
            if args.get("return_order_id", False):
                return_picking_objs = self.env['stock.picking'].sudo().search(
                    [('return_picking_id', '=', picking_obj.id),
                     ('id', '=', int(args.get("return_order_id", False)))])
                if not return_picking_objs:
                    return {
                        "Code": 500,
                        "StatusDescription": "Failed",
                        "Data": {},
                        "ArabicMessage": "رقم امر الاسترجاع غير صحيح",
                        "EnglishMessage": "Return Delivery order ID is not Correct"
                    }
            else:
                return_picking_objs = self.env['stock.picking'].sudo().search(
                    [('return_picking_id', '=', picking_obj.id)])
            return_picking_list = []
            for return_picking_obj in return_picking_objs:
                return_stock_picking_line_list = []
                for return_stock_picking_line_obj in return_picking_obj.move_line_ids_without_package:
                    return_stock_picking_line_list.append(
                        {
                            'return_stock_line_picking_id': return_stock_picking_line_obj.id,
                            "product_id": return_stock_picking_line_obj.product_id.id,
                            'product_name': return_stock_picking_line_obj.product_id.name,
                            'product_img_link': base_url + "/web/binary/download_document?model=product.product&field=image_1920&id=" + str(
                                return_stock_picking_line_obj.product_id.id) + "&filename=image_1920.jpg",
                            "product_qty": return_stock_picking_line_obj.qty_done,
                            "product_uom_id": return_stock_picking_line_obj.product_uom_id.id,
                            "product_uom_name": return_stock_picking_line_obj.product_uom_id.name,
                        }
                    )
                return_stock_picking_move_list = []
                for return_stock_picking_move_obj in return_picking_obj.move_ids_without_package:
                    return_stock_picking_move_list.append(
                        {
                            'return_stock_move_picking_id': return_stock_picking_move_obj.id,
                            "product_id": return_stock_picking_move_obj.product_id.id,
                            'product_name': return_stock_picking_move_obj.product_id.name,
                            'product_img_link': base_url + "/web/binary/download_document?model=product.product&field=image_1920&id=" + str(
                                return_stock_picking_move_obj.product_id.id) + "&filename=image_1920.jpg",
                            "product_qty": return_stock_picking_move_obj.quantity_done,
                            "product_uom_id": return_stock_picking_move_obj.product_uom.id,
                            "product_uom_name": return_stock_picking_move_obj.product_uom.name,
                        }
                    )

                return_picking_list.append({
                    "return_order_id ": return_picking_obj.id,
                    "return_order_name": return_picking_obj.name,
                    "return_order_date": return_picking_obj.scheduled_date if return_picking_obj.scheduled_date else '',
                    "return_order_notes": return_picking_obj.note if return_picking_obj.note else '',
                    "return_order_state": dict(return_picking_obj._fields['state'].selection).get(
                        return_picking_obj.state),
                    "return_order_operation": return_stock_picking_move_list,
                    "return_order_detail_operation": return_stock_picking_line_list,
                })
            stock_picking_list.append({
                "transfer_order_id": picking_obj.id,
                "transfer_order_name": picking_obj.name,
                "transfer_order_date": picking_obj.scheduled_date if picking_obj.scheduled_date else '',
                'transfer_operation_type_id': picking_obj.picking_type_id.id,
                'transfer_operation_type_name': picking_obj.picking_type_id.name,
                'transfer_source_location_id': picking_obj.location_id.id,
                'transfer_source_location_name': picking_obj.location_id.name,
                'transfer_source_dest_id': picking_obj.location_dest_id.id,
                'transfer_source_dest_name': picking_obj.location_dest_id.name,

                "transfer_order_notes": picking_obj.note if picking_obj.note else '',
                "transfer_order_state": dict(picking_obj._fields['state'].selection).get(picking_obj.state),
                'delivery_order_details': stock_picking_move_list,
                "transfer_order_detail_operation": stock_picking_line_list,
                "return_picking_list_count": len(return_picking_list),
                "return_picking_list": return_picking_list
            })

        return {
            "Code": 200,
            "StatusDescription": "Success",
            "Data": stock_picking_list,
            "ArabicMessage": "تم إسترجاع طلبات التحويل للعميل بنجاح",
            "EnglishMessage": "Customer Transfer Orders have been Retrieved Successfully"
        }

    @api.model
    def  do_action_internal_transfer(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        user_obj = self.env['res.users'].browse(args.get('userId'))
        try:
            if args.get("transfer_order_id", False):
                stock_picking_obj = self.env['stock.picking'].sudo().search(
                    [('id', '=', int(args.get("transfer_order_id", False)))])
                if not stock_picking_obj:
                    return {
                        "Code": 500,
                        "StatusDescription": "Failed",
                        "Data": {},
                        "ArabicMessage": "رقم امر التوريد غير صحيح",
                        "EnglishMessage": "Delivery order ID is not correct"
                    }
            else:
                return {
                    "Code": 500,
                    "StatusDescription": "Failed",
                    "Data": {},
                    "ArabicMessage": "رقم امر التوريد غير موجود",
                    "EnglishMessage": "Delivery order ID is not Provided"
                }
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if not args.get("transfer_order_action", ''):
                return {
                    "Code": 500,
                    "StatusDescription": "Failed",
                    "Data": {},
                    "ArabicMessage": "نوع الحركه غير موجود",
                    "EnglishMessage": "Transfer order action is not Provided"
                }
            if args.get("transfer_order_action", '') not in ['done']:
                return {
                    "Code": 500,
                    "StatusDescription": "Failed",
                    "Data": {},
                    "ArabicMessage": "نوع الحركه غير صحيح",
                    "EnglishMessage": "Transfer order action is not correct"
                }
            if args.get("transfer_order_action", '') == 'done':
                stock_picking_obj.with_user(args.get('userId')).sudo().action_confirm()
                stock_picking_obj.with_user(args.get('userId')).sudo().action_assign()
                for move_ids_without_package_obj in stock_picking_obj.move_ids_without_package:
                    move_ids_without_package_obj.quantity_done = move_ids_without_package_obj.product_uom_qty
                # stock_picking_obj.with_user(args.get('userId')).sudo().action_set_quantities_to_reservation()

                action = stock_picking_obj.with_user(args.get('userId')).sudo().button_validate()
                picking_context = dict(self.env.context, default_show_transfers=False,
                                       default_pick_ids=[(4, p.id) for p in stock_picking_obj],
                                       button_validate_picking_ids=[stock_picking_obj.id])
                if action != True:
                    try:
                        backorder_wizard = Form(
                            self.env['stock.backorder.confirmation'].sudo().with_context(action['context'])).save()
                    except Exception as e:
                        backorder_wizard = Form(
                            self.env['stock.backorder.confirmation'].sudo().with_context(picking_context)).save()
                    backorder_wizard.with_user(args.get('userId')).sudo().process()
                stock_picking_obj.with_user(args.get('userId')).sudo().action_accepted()
            # if args.get("transfer_order_action", '') == 'markastodo':
            #     stock_picking_obj.with_user(args.get('userId')).sudo().action_confirm()

            stock_picking_line_list = []
            for stock_picking_line_obj in stock_picking_obj.move_line_ids_without_package:
                stock_picking_line_list.append({
                    'stock_picking_id': stock_picking_line_obj.id,
                    "product_id": stock_picking_line_obj.product_id.id,
                    'product_name': stock_picking_line_obj.product_id.name,
                    'product_img_link': base_url + "/web/binary/download_document?model=product.product&field=image_1920&id=" + str(
                        stock_picking_line_obj.product_id.id) + "&filename=image_1920.jpg",
                    "product_qty": stock_picking_line_obj.qty_done,
                    "reserved_product_qty": stock_picking_line_obj.reserved_uom_qty,
                    "product_uom_id": stock_picking_line_obj.product_uom_id.id,
                    "product_uom_name": stock_picking_line_obj.product_uom_id.name,
                })
            stock_picking_dic = {
                "delivery_order_id ": stock_picking_obj.id,
                "delivery_order_name": stock_picking_obj.name,
                "delivery_order_date": stock_picking_obj.scheduled_date if stock_picking_obj.scheduled_date else '',
                "delivery_order_notes": stock_picking_obj.note if stock_picking_obj.note else '',
                "delivery_order_state": dict(stock_picking_obj._fields['state'].selection).get(stock_picking_obj.state),
                "sales_order_deliveries_count": len(stock_picking_obj),
                # 'delivery_order_details': stock_picking_move_list,
                "delivery_order_detail_operation": stock_picking_line_list,

            }
        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        return api_global_function.return_success_list_api([stock_picking_dic])