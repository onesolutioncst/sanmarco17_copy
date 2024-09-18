 # -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from docxtpl import DocxTemplate
import num2words

split_chr = '\\' if ':' in __file__ else '/'  # if ':' in file_name then I'm running on windows server
import os, base64, io
from odoo.exceptions import UserError, ValidationError

class fleet_contract_template_wizard(models.TransientModel):
    _name = "fleet.contract.template.wizard"

    template_id = fields.Many2one('fleet.contract.template', 'Template',)
    type = fields.Selection(
        string="Type",
        selection=[('sale', 'Sale'), ('purchase', 'Purchase')],)


    def template_download_global(self):
        return self.template_download_fleet_contract()

    def convert_day_name_to_arabic(self, day_name):
        if day_name == 'Monday':
            return 'الاثنين'
        elif day_name == 'Tuesday':
            return 'الثلاثاء'
        elif day_name == 'Wednesday':
            return 'الاربعاء'
        elif day_name == 'Thursday':
            return 'الخميس'
        elif day_name == 'Friday':
            return 'الجمعه'
        elif day_name == 'Saturday':
            return 'السبت'
        elif day_name == 'Sunday':
            return 'الاحد'


    def get_info(self, fleet_contract_obj):
        vehicle_commitment_date_name = ""
        if fleet_contract_obj.sale_id and fleet_contract_obj.sale_id.commitment_date:
            vehicle_commitment_date_name = self.convert_day_name_to_arabic(fleet_contract_obj.sale_id.commitment_date.strftime("%A") )
        if fleet_contract_obj.cost_subtype_id.type == 'sale':
            if (vehicle_commitment_date_name and fleet_contract_obj.buyer.civil_id and fleet_contract_obj.buyer.street and fleet_contract_obj.buyer.mobile and fleet_contract_obj.buyer.country_id and fleet_contract_obj.customer_id.civil_id and fleet_contract_obj.customer_id.street and fleet_contract_obj.customer_id.mobile and fleet_contract_obj.customer_id.country_id):
             return {
                    'name': fleet_contract_obj.name,

                    'date': fleet_contract_obj.date,
                    'start_date': fleet_contract_obj.start_date,
                    'day_name': self.convert_day_name_to_arabic(fleet_contract_obj.day_name),

                    'buyer_name': fleet_contract_obj.buyer.name or '',
                    'buyer_civil_id': fleet_contract_obj.buyer.civil_id or '',
                    'buyer_address': fleet_contract_obj.buyer.street or '',
                    'buyer_mobile': fleet_contract_obj.buyer.mobile or '',
                    'buyer_country': fleet_contract_obj.buyer.country_id.name or '',

                    'customer_name': fleet_contract_obj.customer_id.name or '',
                    'customer_civil_id': fleet_contract_obj.customer_id.civil_id or '',
                    'customer_address': fleet_contract_obj.customer_id.street or '',
                    'customer_mobile': fleet_contract_obj.customer_id.mobile or '',
                    'customer_country': fleet_contract_obj.customer_id.country_id.name or '',

                    # Contract Info
                    'vehicle_name': fleet_contract_obj.vehicle_id.name,
                    'vehicle_model_name': fleet_contract_obj.vehicle_id.model_id.name,
                    'vehicle_model_factoru': fleet_contract_obj.vehicle_id.model_id.brand_id.name,
                    'vehicle_license_plate': fleet_contract_obj.vehicle_id.license_plate,
                    'vehicle_model_year': fleet_contract_obj.vehicle_id.model_year,
                    'vehicle_color': fleet_contract_obj.vehicle_id.color,
                    'vehicle_odoometer': fleet_contract_obj.vehicle_id.odometer,
                    'vehicle_country': fleet_contract_obj.vehicle_id.vehicle_country_id.name,
                    'vehicle_chassis_number': fleet_contract_obj.vehicle_id.chassis_number,
                    'vehicle_en_num': fleet_contract_obj.vehicle_id.en_num,
                    'vehicle_license_number': fleet_contract_obj.vehicle_id.license,
                    'vehicle_license_i': fleet_contract_obj.license_i.name,
                    'vehicle_net_car_value': fleet_contract_obj.vehicle_id.net_car_value,
                    'vehicle_net_car_value_text': num2words.num2words(fleet_contract_obj.vehicle_id.net_car_value, lang='ar'),
                    'vehicle_sale_car_value': fleet_contract_obj.vehicle_id.sale_car_value,
                    'vehicle_sale_car_value_text': num2words.num2words(fleet_contract_obj.vehicle_id.sale_car_value, lang='ar'),
                    'vehicle_down_payment': fleet_contract_obj.down_payment,
                    'vehicle_rem_payment': fleet_contract_obj.rem_payment,
                    'vehicle_commitment_date': fleet_contract_obj.sale_id.commitment_date.date() if fleet_contract_obj.sale_id and fleet_contract_obj.sale_id.commitment_date else '',
                    'vehicle_commitment_date_name': vehicle_commitment_date_name,
                    'vehicle_commitment_date_time': str(fleet_contract_obj.sale_id.commitment_date.time())  if fleet_contract_obj.sale_id and fleet_contract_obj.sale_id.commitment_date else '',


                    'user_name': fleet_contract_obj.user_id.name,
                    'type': fleet_contract_obj.cost_subtype_id.name,
                    'invoice_number': fleet_contract_obj.invoice_id.name,
                    'ins_ref': fleet_contract_obj.ins_ref,
                    'amount': fleet_contract_obj.amount,
                    'net_car_value': fleet_contract_obj.net_car_value,
                    'sale_car_value': fleet_contract_obj.sale_car_value,
                    'cost_generated': fleet_contract_obj.cost_generated,
                    'vehicle_name': fleet_contract_obj.vehicle_id.name,
                    'driver_name': fleet_contract_obj.purchaser_id.name,
                    'expiration_date': fleet_contract_obj.expiration_date,
                    'notes': fleet_contract_obj.notes,
                    'en_num': fleet_contract_obj.en_num,
                    'factory': fleet_contract_obj.factory,
                    'license': fleet_contract_obj.license,
                    'license_i': fleet_contract_obj.license_i,
                    'down_payment': fleet_contract_obj.down_payment,
                    'rem_payment': fleet_contract_obj.rem_payment,

                    'day_name_sale': fleet_contract_obj.day_name_sale  or '',
                    'time_sale': fleet_contract_obj.time_sale  or '',
                }
            else:
                raise ValidationError(
                    _(f"Delivery Date ,Buyer Civil, Buyer Street, Buyer Mobile, Buyer Country, Customer Civil, Customer Street, Customer Mobile, Customer Country."))
        elif fleet_contract_obj.cost_subtype_id.type == 'purchase':
            if (fleet_contract_obj.insurer_id.civil_id and fleet_contract_obj.insurer_id.street and fleet_contract_obj.insurer_id.mobile and fleet_contract_obj.insurer_id.country_id and fleet_contract_obj.buyer.civil_id and fleet_contract_obj.buyer.street and fleet_contract_obj.buyer.mobile and fleet_contract_obj.buyer.country_id):
             return {
                    'name': fleet_contract_obj.name,

                    'date': fleet_contract_obj.date,
                    'start_date': fleet_contract_obj.start_date,
                    'day_name': self.convert_day_name_to_arabic(fleet_contract_obj.day_name),

                    'buyer_name': fleet_contract_obj.buyer.name or '',
                    'buyer_civil_id': fleet_contract_obj.buyer.civil_id or '',
                    'buyer_address': fleet_contract_obj.buyer.street or '',
                    'buyer_mobile': fleet_contract_obj.buyer.mobile or '',
                    'buyer_country': fleet_contract_obj.buyer.country_id.name or '',

                    'vendor_name': fleet_contract_obj.insurer_id.name or '',
                    'vendor_civil_id': fleet_contract_obj.insurer_id.civil_id or '',
                    'vendor_address': fleet_contract_obj.insurer_id.street or '',
                    'vendor_mobile': fleet_contract_obj.insurer_id.mobile or '',
                    'vendor_country': fleet_contract_obj.insurer_id.country_id.name or '',

                    # Contract Info
                    'vehicle_name': fleet_contract_obj.vehicle_id.name,
                    'vehicle_model_name': fleet_contract_obj.vehicle_id.model_id.name,
                    'vehicle_model_factoru': fleet_contract_obj.vehicle_id.model_id.brand_id.name,
                    'vehicle_license_plate': fleet_contract_obj.vehicle_id.license_plate,
                    'vehicle_model_year': fleet_contract_obj.vehicle_id.model_year,
                    'vehicle_color': fleet_contract_obj.vehicle_id.color,
                    'vehicle_odoometer': fleet_contract_obj.vehicle_id.odometer,
                    'vehicle_country': fleet_contract_obj.vehicle_id.vehicle_country_id.name,
                    'vehicle_chassis_number': fleet_contract_obj.vehicle_id.chassis_number,
                    'vehicle_en_num': fleet_contract_obj.vehicle_id.en_num,
                    'vehicle_license_number': fleet_contract_obj.vehicle_id.license,
                    'vehicle_license_i': fleet_contract_obj.license_i.name,
                    'vehicle_net_car_value': fleet_contract_obj.vehicle_id.net_car_value,
                    'vehicle_net_car_value_text': num2words.num2words(fleet_contract_obj.vehicle_id.net_car_value, lang='ar'),
                    'vehicle_sale_car_value': fleet_contract_obj.vehicle_id.sale_car_value,
                    'vehicle_sale_car_value_text': num2words.num2words(fleet_contract_obj.vehicle_id.sale_car_value, lang='ar'),
                    'vehicle_down_payment': fleet_contract_obj.down_payment,
                    'vehicle_rem_payment': fleet_contract_obj.rem_payment,
                    'vehicle_commitment_date': fleet_contract_obj.sale_id.commitment_date.date() if fleet_contract_obj.sale_id and fleet_contract_obj.sale_id.commitment_date else '',
                    'vehicle_commitment_date_name': vehicle_commitment_date_name,
                    'vehicle_commitment_date_time': str(fleet_contract_obj.sale_id.commitment_date.time())  if fleet_contract_obj.sale_id and fleet_contract_obj.sale_id.commitment_date else '',


                    'user_name': fleet_contract_obj.user_id.name,
                    'type': fleet_contract_obj.cost_subtype_id.name,
                    'invoice_number': fleet_contract_obj.invoice_id.name,
                    'ins_ref': fleet_contract_obj.ins_ref,
                    'amount': fleet_contract_obj.amount,
                    'net_car_value': fleet_contract_obj.net_car_value,
                    'sale_car_value': fleet_contract_obj.sale_car_value,
                    'cost_generated': fleet_contract_obj.cost_generated,
                    'vehicle_name': fleet_contract_obj.vehicle_id.name,
                    'driver_name': fleet_contract_obj.purchaser_id.name,
                    'expiration_date': fleet_contract_obj.expiration_date,
                    'notes': fleet_contract_obj.notes,
                    'en_num': fleet_contract_obj.en_num,
                    'factory': fleet_contract_obj.factory,
                    'license': fleet_contract_obj.license,
                    'license_i': fleet_contract_obj.license_i,
                    'down_payment': fleet_contract_obj.down_payment,
                    'rem_payment': fleet_contract_obj.rem_payment,

                    'day_name_sale': fleet_contract_obj.day_name_sale  or '',
                    'time_sale': fleet_contract_obj.time_sale  or '',
                }
            else:
                raise ValidationError(
                    _(f"Vendor Civil, Vendor Street, Vendor Mobile, Vendor Country, Buyer Civil, Buyer Street, Buyer Mobile, Buyer Country."))
        else:
            return {
            'name': fleet_contract_obj.name,

            'date': fleet_contract_obj.date,
            'start_date': fleet_contract_obj.start_date,
            'day_name': self.convert_day_name_to_arabic(fleet_contract_obj.day_name),

            'buyer_name': fleet_contract_obj.buyer.name or '',
            'buyer_civil_id': fleet_contract_obj.buyer.civil_id or '',
            'buyer_address': fleet_contract_obj.buyer.street or '',
            'buyer_mobile': fleet_contract_obj.buyer.mobile or '',
            'buyer_country': fleet_contract_obj.buyer.country_id.name or '',

            'customer_name': fleet_contract_obj.customer_id.name or '',
            'customer_civil_id': fleet_contract_obj.customer_id.civil_id or '',
            'customer_address': fleet_contract_obj.customer_id.street or '',
            'customer_mobile': fleet_contract_obj.customer_id.mobile or '',
            'customer_country': fleet_contract_obj.customer_id.country_id.name or '',

            'vendor_name': fleet_contract_obj.insurer_id.name or '',
            'vendor_civil_id': fleet_contract_obj.insurer_id.civil_id or '',
            'vendor_address': fleet_contract_obj.insurer_id.street or '',
            'vendor_mobile': fleet_contract_obj.insurer_id.mobile or '',
            'vendor_country': fleet_contract_obj.insurer_id.country_id.name or '',

            # Contract Info
            'vehicle_name': fleet_contract_obj.vehicle_id.name,
            'vehicle_model_name': fleet_contract_obj.vehicle_id.model_id.name,
            'vehicle_model_factoru': fleet_contract_obj.vehicle_id.model_id.brand_id.name,
            'vehicle_license_plate': fleet_contract_obj.vehicle_id.license_plate,
            'vehicle_model_year': fleet_contract_obj.vehicle_id.model_year,
            'vehicle_color': fleet_contract_obj.vehicle_id.color,
            'vehicle_country': fleet_contract_obj.vehicle_id.vehicle_country_id.name,
            'vehicle_chassis_number': fleet_contract_obj.vehicle_id.chassis_number,
            'vehicle_en_num': fleet_contract_obj.vehicle_id.en_num,
            'vehicle_license_number': fleet_contract_obj.vehicle_id.license,
            'vehicle_license_i': fleet_contract_obj.license_i.name,
            'vehicle_net_car_value': fleet_contract_obj.vehicle_id.net_car_value,
            'vehicle_sale_car_value': fleet_contract_obj.vehicle_id.sale_car_value,
            'vehicle_down_payment': fleet_contract_obj.down_payment,
            'vehicle_rem_payment': fleet_contract_obj.rem_payment,
            'vehicle_commitment_date': fleet_contract_obj.sale_id.commitment_date.date() if fleet_contract_obj.sale_id and fleet_contract_obj.sale_id.commitment_date else '',
            'vehicle_commitment_date_name': vehicle_commitment_date_name,
            'vehicle_commitment_date_time': str(
                fleet_contract_obj.sale_id.commitment_date.time()) if fleet_contract_obj.sale_id and fleet_contract_obj.sale_id.commitment_date else '',

            'user_name': fleet_contract_obj.user_id.name,
            'type': fleet_contract_obj.cost_subtype_id.name,
            'invoice_number': fleet_contract_obj.invoice_id.name,
            'ins_ref': fleet_contract_obj.ins_ref,
            'amount': fleet_contract_obj.amount,
            'net_car_value': fleet_contract_obj.net_car_value,
            'sale_car_value': fleet_contract_obj.sale_car_value,
            'cost_generated': fleet_contract_obj.cost_generated,
            'vehicle_name': fleet_contract_obj.vehicle_id.name,
            'driver_name': fleet_contract_obj.purchaser_id.name,
            'expiration_date': fleet_contract_obj.expiration_date,
            'notes': fleet_contract_obj.notes,
            'en_num': fleet_contract_obj.en_num,
            'factory': fleet_contract_obj.factory,
            'license': fleet_contract_obj.license,
            'license_i': fleet_contract_obj.license_i,
            'down_payment': fleet_contract_obj.down_payment,
            'rem_payment': fleet_contract_obj.rem_payment,

            'day_name_sale': fleet_contract_obj.day_name_sale or '',
            'time_sale': fleet_contract_obj.time_sale or '',
        }


    def template_download_fleet_contract(self):

        #read the template content, save it to a temp file
        # tpl2 = tempfile.NamedTemporaryFile()
        fl = split_chr.join(__file__.split(split_chr)[:-2])+os.sep
        # fl += '/static/docx/%s' % self.template_id.name
        fl += os.path.join('static','docx', self.template_id.name)
        fl = os.path.join('/tmp/', self.template_id.name)
        tpl = open(fl, "wb")
        tpl.write(base64.b64decode(self.template_id.template))
        #create the doc using the created temp file
        doc = DocxTemplate(tpl.name)
        tpl.close()

        #render
        fleet_contract_obj = self.env[self.env.context['active_model']].browse(self.env.context['active_id'])
        doc.render(self.get_info(fleet_contract_obj))
        #save
        file_stream = io.BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        file_name = 'Fleet Contract - %s.docx'%(fleet_contract_obj.vehicle_id.name)
        #download
        return self.env['binary.downloads'].get_download_url({
            # 'filename': convert(file_name,'output.pdf'),
            'filename': file_name,
            'content': base64.encodebytes(file_stream.read()),
            })
