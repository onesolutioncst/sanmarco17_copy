from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging
from . import api_global_function

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"
class ProductTemplate(models.Model):
    _inherit = "product.template"
    come_from = fields.Char('Come From')
    product_images_ids = fields.One2many('product.images', 'product_id', 'Images')

class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def get_all_products(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_SY'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        domain = [('detailed_type','=','product')]
        if args.get("product_id", False):
            domain.append(('id', '=', args.get("product_id", False)))
        if args.get("product_type", False):
            if args.get("product_type", False) not in ['consu', 'service', 'product', 'event']:
                return api_global_function.return_failed_request_vals(
                    "Wrong Product Type it must be 'consu (Consumable)',"
                    "'service(Service)','product(Storable Product)','event(Event Ticket)'",
                    "عفوا نوع المنتج غير صحيح")
            domain.append(('detailed_type', '=', args.get("product_type", False)))
        if args.get("categ_id", False):
            if not self.env['product.category'].sudo().search([('id', '=', args.get("categ_id", False))]):
                return api_global_function.return_failed_request_vals(
                    "Wrong Category ID Please Cjeck",
                    "عفوا تصنيف المنتج غير صحيح")
            domain.append(('categ_id', '=', args.get("categ_id", False)))

        product_template_objs = self.env['product.product'].sudo().search(domain)
        result = []
        for product_template_obj in product_template_objs:
            product_images_list = []
            vendor_category_list = []
            sub_vendor_category_list = []
            optional_product_list = []
            for product_images_obj in product_template_obj.product_images_ids:
                product_images_list.append(product_images_obj.image_link)
            for optional_product_obj in product_template_obj.optional_product_ids:
                optional_product_list.append({
                    'id': optional_product_obj.id,
                    'name': optional_product_obj.name or '',
                })
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            result.append({
                'id': product_template_obj.id,
                'product_tmpl_id': product_template_obj.id,
                'name': product_template_obj.name or '',
                'image': base_url + "/web/binary/download_document?model=product.product&field=image_1920&id=" + str(
                    product_template_obj.id) + "&filename=image_1920.jpg" if product_template_obj.image_1920 else '',
                'fullname': product_template_obj.display_name or '',
                'can_be_sold': product_template_obj.sale_ok,
                'can_be_purchase': product_template_obj.purchase_ok,
                'product_type': product_template_obj.detailed_type,
                'invoice_policy': product_template_obj.invoice_policy,
                'unit_of_measure': {'id': product_template_obj.uom_id.id,
                                    'name': product_template_obj.uom_id.name} if product_template_obj.uom_id else {},
                'sales_price': product_template_obj.list_price,
                'currency': {'id': product_template_obj.currency_id.id,
                             'name': product_template_obj.currency_id.name} if product_template_obj.currency_id else {},
                'cost_currency': {'id': product_template_obj.cost_currency_id.id,
                                  'name': product_template_obj.cost_currency_id.name} if product_template_obj.cost_currency_id else {},
                'product_category': {'id': product_template_obj.categ_id.id,
                                     'name': product_template_obj.categ_id.name} if product_template_obj.categ_id else {},
                'internal_reference': product_template_obj.default_code or '',
                'barcode': product_template_obj.barcode or '',
                'sale_description': product_template_obj.description_sale or '',
                'purchase_description': product_template_obj.description_purchase or '',
                'product_images_list': product_images_list,
            })
        return api_global_function.return_success_list_api(result)

    def check_product_vals(self, args):
        product_vals = {'detailed_type': 'product'}
        if args.get('expenseproduct', False) == True:
            product_vals.update({'can_be_expensed': True})
        if args.get("RequestID", False):
            product_vals.update({'id': args.get("RequestID", False)})
            if args.get('barcode', False):
                if self.env['product.product'].sudo().search([('barcode', '=', args.get('barcode', False))]):
                    return False, api_global_function.return_failed_request_vals(
                        "Product Barcode can only be assigned to one product",
                        "عفوا باركود المنتج موجود مسبقا")
                product_vals.update({'barcode': args.get('barcode', False)})
        try:
            if not args.get('name', False) and not args.get("RequestID", False):
                return False, api_global_function.return_failed_request_vals("Product Name Not provided",
                                                                             "عفوا اسم المنتج مش موجود")
            product_vals.update({'name': args.get('name', False)})

            if not args.get('come_from', False) and not args.get("RequestID", False):
                return False, api_global_function.return_failed_request_vals("Come From Not provided",
                                                                             "عفوا المصدر مش موجود")
            product_vals.update({'come_from': args.get('come_from', False)})

            if args.get('product_type', False):
                if args.get("product_type", False) not in ['consu', 'service', 'product', 'event']:
                    return api_global_function.return_failed_request_vals(
                        "Wrong Product Type it must be 'consu (Consumable)',"
                        "'service(Service)','product(Storable Product)','event(Event Ticket)'",
                        "عفوا نوع المنتج غير صحيح")
                product_vals.update({'detailed_type': args.get('product_type', False)})
            if not args.get('sale_price', False) and not args.get("RequestID", False):
                return False, api_global_function.return_failed_request_vals("Product Sale Price Not provided",
                                                                             "عفوا سعر البيع للمنتج مش موجود")
            product_vals.update({'list_price': args.get('sale_price', False)})

            if not args.get('internal_reference', False) and not args.get("RequestID", False):
                return False, api_global_function.return_failed_request_vals("Product internal reference Not provided",
                                                                             "عفوا الرقم المرجعى للمنتج مش موجود")
            product_vals.update({'default_code': args.get('internal_reference', False)})

            if not args.get('barcode', False) and not args.get("RequestID", False):
                return False, api_global_function.return_failed_request_vals("Product Barcode Not provided",
                                                                             "عفوا باركود المنتج مش موجود")
            if self.env['product.product'].sudo().search([('barcode', '=', args.get('barcode', False))]):
                return False, api_global_function.return_failed_request_vals(
                    "Product Barcode can only be assigned to one product",
                    "عفوا باركود المنتج موجود مسبقا")
            product_vals.update({'barcode': args.get('barcode', False)})

            if args.get('sale_description', False):
                product_vals.update({'description_sale': args.get('sale_description', False)})
            if args.get('purchase_description', False):
                product_vals.update({'description_purchase': args.get('purchase_description', False)})

            if not args.get('image', False) and not args.get("RequestID", False):
                return False, api_global_function.return_failed_request_vals("Product Image Is Not provided",
                                                                             "عفوا صورة المنتج غير موجودة")
            product_vals.update({'image_1920': args.get('image', False)})

            if args.get('sku', False):
                product_vals.update({'sku': args.get('sku', False)})
            if args.get('fast_number', False):
                product_vals.update({'x_fast_number': args.get('fast_number', False)})
            if args.get('serial_number', False):
                product_vals.update({'x_serial_number': args.get('serial_number', False)})
            if not args.get('arabic_name', False) and not args.get("RequestID", False):
                return False, api_global_function.return_failed_request_vals("Product Name in Arabic Not provided",
                                                                             "عفوا اسم المنتج بالعربي غير موجود")
            product_vals.update({'arabic_name': args.get('arabic_name', False)})

            if not args.get('vendor_category_ids', []) and not args.get("RequestID", False):
                return False, api_global_function.return_failed_request_vals("Vendor Category Not provided",
                                                                             "عفوا نوع المورد غير موجود")
            vendor_category_list = []
            for vendor_category_id in args.get('vendor_category_ids', []):
                if not self.env['vendor.category'].sudo().search([('id', '=', int(vendor_category_id))]):
                    return False, api_global_function.return_failed_request_vals("Vendor Category Not Correct",
                                                                                 "عفوا نوع المورد غير صحيح")
                vendor_category_list.append((4, vendor_category_id))
            product_vals.update({'vendor_category_ids': vendor_category_list})

            if args.get('sub_category_ids', []):
                sub_vendor_category_list = []
                for sub_category_id in args.get('sub_category_ids', []):
                    if not self.env['vendor.category'].sudo().search([('id', '=', int(sub_category_id))]):
                        return False, api_global_function.return_failed_request_vals("Sub Vendor Category Not Correct",
                                                                                     "عفوا نوع المورد غير صحيح")
                    sub_vendor_category_list.append((4, sub_category_id))
                product_vals.update({'sub_category_ids': sub_vendor_category_list})

            if not args.get('pyzah_product_type', False) and not args.get("RequestID", False):
                return False, api_global_function.return_failed_request_vals("Product Type Not provided",
                                                                             "عفوا نوع المنتج غير موجود")
            if args.get("pyzah_product_type", False) not in ['buy', 'register']:
                return api_global_function.return_failed_request_vals(
                    "Wrong Pyzah Product Type it must be 'buy (Buy)','register (Register)'",
                    "عفوا نوع المنتج غير صحيح")
            product_vals.update({'pyzah_product_type': args.get('pyzah_product_type', False)})

            if args.get('product_label', False):
                product_vals.update({'product_label': args.get('product_label', False)})
            if args.get('product_label_color', False):
                product_vals.update({'product_label_color': args.get('product_label_color', False)})
            if args.get('arabic_product_label', False):
                product_vals.update({'arabic_product_label': args.get('arabic_product_label', False)})
            if args.get('discount_type', False):
                if args.get("discount_type", False) not in ['fixed', 'percent']:
                    return api_global_function.return_failed_request_vals(
                        "Wrong Discount Type it must be 'fixed (Fixed)','percent (percentage)'",
                        "عفوا نوع الخصم غير صحيح")
                product_vals.update({'discount_type': args.get('discount_type', False)})
            if args.get('fixed_discount', False):
                product_vals.update({'fixed_discount': args.get('fixed_discount', False)})
            # if args.get('percent_discount', False):
            #     product_vals.update({'percent_discount': args.get('percent_discount', False)})
            if args.get('product_start_time', False):
                product_vals.update({'product_start_time': args.get('product_start_time', False)})
            if args.get('product_end_time', False):
                product_vals.update({'product_end_time': args.get('product_end_time', False)})
            if args.get('product_video_link', False):
                product_vals.update({'product_video_link': args.get('product_video_link', False)})
            if args.get('product_video_file', False):
                product_vals.update({'product_video_file': args.get('product_video_file', False)})
            if args.get('product_depth', False):
                product_vals.update({'product_depth': args.get('product_depth', False)})
            if args.get('product_width', False):
                product_vals.update({'product_width': args.get('product_width', False)})
            if args.get('product_height', False):
                product_vals.update({'product_height': args.get('product_height', False)})
            if args.get('product_weight', False):
                product_vals.update({'product_weight': args.get('product_weight', False)})
            if args.get('product_short_description', False):
                product_vals.update({'product_short_description': args.get('product_short_description', False)})
            if args.get('product_short_description_arabic', False):
                product_vals.update(
                    {'product_short_description_arabic': args.get('product_short_description_arabic', False)})
            if args.get('pyzah_product_description', False):
                product_vals.update({'pyzah_product_description': args.get('pyzah_product_description', False)})
            if args.get('pyzah_product_description_arabic', False):
                product_vals.update(
                    {'pyzah_product_description_arabic': args.get('pyzah_product_description_arabic', False)})
            if args.get('product_faq', False):
                product_vals.update({'product_faq': args.get('product_faq', False)})
            if args.get('product_faq_arabic', False):
                product_vals.update({'product_faq_arabic': args.get('product_faq_arabic', False)})
            if args.get('optional_product_list', False):
                optional_product_ll = []
                for optional_product_id in args.get('optional_product_list', False):
                    if not self.env['product.product'].sudo().search([('id','=',optional_product_id)]):
                        return api_global_function.return_failed_request_vals(
                            "Product Id is not correct",
                            "رقم الصنف غير صحيح")
                    optional_product_ll.append((4, optional_product_id))
                product_vals.update({'optional_product_ids': optional_product_ll})
        except Exception as e:
            arabic_message = "%s  " % _(str(e)),
            englishmessage = "%s." % _(str(e))
            return False, api_global_function.return_failed_request_vals(englishmessage, arabic_message)
        return True, product_vals

    def add_update_product(self, **args):
        request_id = args.get("RequestID", False)
        check_vals, product_vals = self.check_product_vals(args)
        if not check_vals:
            return product_vals
        try:
            if not request_id:
                product_template_obj = self.with_user(args.get('userId')).sudo().create(product_vals)
            else:
                # Update Request ID
                product_template_obj = self.with_user(args.get('userId')).sudo().browse(request_id)
                product_template_obj.with_user(args.get('userId')).sudo().write(product_vals)
            if args.get('product_images', []):
                for product_images in args.get('product_images', []):
                    if not product_images.get('image_link', False):
                        return False, api_global_function.return_failed_request_vals(
                            "Product Image Link is not provided",
                            "عفوا لينك الصورة بالمنتج غير موجودة ")
                    product_template_image_obj = self.env['product.images'].with_user(args.get('userId')).sudo().create(
                        {"product_id": product_template_obj.product_tmpl_id.id,
                         "image_link": product_images.get('image_link', "")})
                    # product_images_dic['image_link'] = product_images.get('image_link', False)
                    # product_images_list.append((0, 0, product_images_dic))
                # product_vals.update({'product_images_ids': product_images_list})
        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        if not request_id:
            return api_global_function.return_success_creation_api(product_template_obj.id, product_template_obj.id)
        else:
            return api_global_function.return_success_update_api(product_template_obj.id, product_template_obj.id)

    def add_product_image(self, **args):
        if not args.get("product_id", False):
            return False, api_global_function.return_failed_request_vals(
                "Product ID is empty please check",
                "عفوا رقم الصنف غير موجود ")
        try:
            product_product_obj = self.with_user(args.get('userId')).sudo().browse(int(args.get("product_id", False)))
            if not args.get('product_images', []):
                return False, api_global_function.return_failed_request_vals(
                    "Product Images is empty please check",
                    "عفوا صور الصنف غير موجود ")
            if args.get('product_images', []):
                for product_images in args.get('product_images', []):
                    if not product_images.get('image_link', False):
                        return False, api_global_function.return_failed_request_vals(
                            "Product Image Link is not provided",
                            "عفوا لينك الصورة بالمنتج غير موجودة ")
                    product_template_image_obj = self.env['product.images'].with_user(args.get('userId')).sudo().create(
                        {"product_id": product_product_obj.product_tmpl_id.id,
                         "image_link": product_images.get('image_link', "")})
        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        return api_global_function.return_success_creation_api(product_product_obj.id, product_product_obj.id)

    @api.model
    def get_all_expense_categories(self, **args):
        lang = args.get('lang')
        if lang == 'ar':
            lang = 'ar_001'
        elif lang == 'en':
            lang = 'en_US'
        else:
            return api_global_function.return_failed_request_vals("Wrong Language Name", "عفوا اللغه غير مدعومه")
        domain = [('can_be_expensed','=',True)]
        if args.get("expense_category_id", False):
            domain.append(('id', '=', args.get("expense_category_id", False)))
        if args.get("product_type", False):
            if args.get("product_type", False) not in ['consu', 'service', 'product', 'event']:
                return api_global_function.return_failed_request_vals(
                    "Wrong Product Type it must be 'consu (Consumable)',"
                    "'service(Service)','product(Storable Product)','event(Event Ticket)'",
                    "عفوا نوع المنتج غير صحيح")
            domain.append(('detailed_type', '=', args.get("product_type", False)))
        if args.get("categ_id", False):
            if not self.env['product.category'].sudo().search([('id', '=', args.get("categ_id", False))]):
                return api_global_function.return_failed_request_vals(
                    "Wrong Category ID Please Cjeck",
                    "عفوا تصنيف المنتج غير صحيح")
            domain.append(('categ_id', '=', args.get("categ_id", False)))

        product_template_objs = self.env['product.product'].with_context(lang=lang).sudo().search(domain)
        result = []
        for product_template_obj in product_template_objs:
            product_images_list = []
            vendor_category_list = []
            sub_vendor_category_list = []
            optional_product_list = []
            for product_images_obj in product_template_obj.product_images_ids:
                product_images_list.append(product_images_obj.image_link)
            for optional_product_obj in product_template_obj.optional_product_ids:
                optional_product_list.append({
                    'id': optional_product_obj.id,
                    'name': optional_product_obj.name or '',
                })
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            result.append({
                'expense_category_id': product_template_obj.id,
                # 'product_tmpl_id': product_template_obj.id,
                'expense_category_name': product_template_obj.name or '',
                'image': base_url + "/web/binary/download_document?model=product.product&field=image_1920&id=" + str(
                    product_template_obj.id) + "&filename=image_1920.jpg" if product_template_obj.image_1920 else '',
                'expense_category_fullname': product_template_obj.display_name or '',
                # 'can_be_sold': product_template_obj.sale_ok,
                # 'can_be_purchase': product_template_obj.purchase_ok,
                'product_type': product_template_obj.detailed_type,
                # 'invoice_policy': product_template_obj.invoice_policy,
                # 'unit_of_measure': {'id': product_template_obj.uom_id.id,
                #                     'name': product_template_obj.uom_id.name} if product_template_obj.uom_id else {},
                # 'sales_price': product_template_obj.list_price,
                # 'currency': {'id': product_template_obj.currency_id.id,
                #              'name': product_template_obj.currency_id.name} if product_template_obj.currency_id else {},
                # 'cost_currency': {'id': product_template_obj.cost_currency_id.id,
                #                   'name': product_template_obj.cost_currency_id.name} if product_template_obj.cost_currency_id else {},
                # 'product_category': {'id': product_template_obj.categ_id.id,
                #                      'name': product_template_obj.categ_id.name} if product_template_obj.categ_id else {},
                'internal_reference': product_template_obj.default_code or '',
                # 'barcode': product_template_obj.barcode or '',
                # 'sale_description': product_template_obj.description_sale or '',
                # 'purchase_description': product_template_obj.description_purchase or '',
                # 'product_images_list': product_images_list,
            })
        return api_global_function.return_success_list_api(result)
    @api.model
    def add_update_expense_product(self, **args):
        request_id = args.get("RequestID", False)
        args.update({'expenseproduct': True})
        check_vals, product_vals = self.check_product_vals(args)
        if not check_vals:
            return product_vals
        try:
            if not request_id:
                product_template_obj = self.with_user(args.get('userId')).sudo().create(product_vals)
            else:
                # Update Request ID
                product_template_obj = self.with_user(args.get('userId')).sudo().browse(request_id)
                product_template_obj.with_user(args.get('userId')).sudo().write(product_vals)
            if args.get('product_images', []):
                for product_images in args.get('product_images', []):
                    if not product_images.get('image_link', False):
                        return False, api_global_function.return_failed_request_vals(
                            "Product Image Link is not provided",
                            "عفوا لينك الصورة بالمنتج غير موجودة ")
                    product_template_image_obj = self.env['product.images'].with_user(args.get('userId')).sudo().create(
                        {"product_id": product_template_obj.product_tmpl_id.id,
                         "image_link": product_images.get('image_link', "")})
                    # product_images_dic['image_link'] = product_images.get('image_link', False)
                    # product_images_list.append((0, 0, product_images_dic))
                # product_vals.update({'product_images_ids': product_images_list})
        except Exception as e:
            self.env.cr.rollback()
            return api_global_function.return_failed_api(_(str(e)))
        if not request_id:
            return api_global_function.return_success_creation_api(product_template_obj.id, product_template_obj.id)
        else:
            return api_global_function.return_success_update_api(product_template_obj.id, product_template_obj.id)
