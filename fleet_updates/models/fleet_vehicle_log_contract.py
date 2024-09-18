from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FleetVehicleLogContract(models.Model):
    _inherit = 'fleet.vehicle.log.contract'

    day_name_sale = fields.Char(string="Day Sale", required=False, compute='_compute_day_sale')
    time_sale = fields.Char(string="Time Sale", required=False, compute='_compute_day_sale')
    day_name = fields.Char(string="Day", required=False, compute='_compute_day')
    en_num = fields.Char(string="Engine number", required=False, related='vehicle_id.en_num', store=True)
    factory = fields.Many2one('fleet.vehicle.model.brand', string="The Factory", required=False,
                              related='vehicle_id.model_id.brand_id', store=True)
    license = fields.Char(string="License Number", required=False, related='vehicle_id.license', store=True)
    license_i = fields.Many2one('res.partner', string="Licence Issuance",)
    buyer = fields.Many2one('res.partner', string="Buyer" )
    down_payment = fields.Float(string="Down payment",)
    rem_payment = fields.Float(string="Remaining Payment")
    customer_id = fields.Many2one("res.partner", "Customer", )
    type = fields.Selection("Type", related='cost_subtype_id.type', stroe=True, )
    sale_id = fields.Many2one("sale.order", "Sale Order")
    purchase_id = fields.Many2one("purchase.order", "Purchase Order")
    invoice_id = fields.Many2one("account.move", "Invoice")
    net_car_value = fields.Float(string='Purchase Value', related='vehicle_id.net_car_value')
    sale_car_value = fields.Float(string='Sales Value', related='vehicle_id.sale_car_value')
    can_edit_resp = fields.Boolean(string="Can Edit Contract Responsible", compute='_compute_can_edit_resp')
    fleet_owner = fields.Many2one('res.partner', string='Fleet Owner', copy=False)

    def unlink(self):
        for record in self:
            if record.sale_id or record.purchase_id or record.invoice_id:
                raise ValidationError(_("Sorry you can't delete this contract as theres Order/Invoice on it "))
        return super(FleetVehicleLogContract, self).unlink()

    @api.depends()
    def _compute_can_edit_resp(self):
        for record in self:
            if self.user_has_groups('one_fleet_custom.can_edit_contract_responsible'):
                record.can_edit_resp = True
            else:
                record.can_edit_resp = False
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

    @api.depends('start_date')
    def _compute_day(self):
        for record in self:
            if record.start_date:
                record.day_name = self.convert_day_name_to_arabic(record.start_date.strftime("%A"))
            else:
                record.day_name = ''

    @api.depends('sale_id')
    def _compute_day_sale(self):
        for record in self:
            if record.sale_id:
                record.day_name_sale = record.sale_id.date_order.strftime("%A")
                record.time_sale = record.sale_id.date_order.strftime("%H:%M")
            else:
                record.day_name_sale = ''
                record.time_sale = ''

    def unlink(self):
        for record in self:
            if record.state == 'done':
                raise ValidationError(_("Can't delete this record as it's in done state"))
            if record.sale_id:
                raise ValidationError(_("Can't delete this record as theres Sale order created"))
            if record.purchase_id:
                raise ValidationError(_("Can't delete this record as theres Purchase order created"))
        return super(FleetVehicleLogContract, self).unlink()

    def run(self):
        self.state = 'running'

    def done(self):
        self.state = 'done'

    def cancel(self):
        self.state = 'cancelled'

    def reset_to_draft(self):
        if self.purchase_id and self.purchase_id.state not in ['purchase', 'done']:
            self.purchase_id.button_cancel()
            self.purchase_id.unlink()
        if self.purchase_id and self.purchase_id.state in ['purchase', 'done']:
            raise ValidationError(_("Sorry theres purchase order in purchase or done state, please set it to draft"))
        if self.sale_id and self.sale_id.state not in ['sale', 'done']:
            self.sale_id.action_cancel()
            self.sale_id.unlink()
        if self.sale_id and self.sale_id.state in ['sale', 'done']:
            raise ValidationError(_("Sorry theres sale order in sale or done state, please set it to draft"))

        self.state = 'new'
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

    @api.model
    def create(self, vals):
        if 'vehicle_id' in vals and vals.get('vehicle_id') and 'cost_subtype_id' in vals and vals.get(
                'cost_subtype_id'):
            vehicle_obj = self.env['fleet.vehicle'].browse(vals.get('vehicle_id'))
            cost_subtype_obj = self.env['fleet.service.type'].browse(vals.get('cost_subtype_id'))
            if vehicle_obj.state_id and not vehicle_obj.state_id.create_fleet_contract and cost_subtype_obj.type == 'sale':
                raise ValidationError(_("Sorry you can't create sale order , please check Vehicle Status"))
        return super(FleetVehicleLogContract, self).create(vals)

    def create_order(self):
        self.ensure_one()
        if self.cost_subtype_id:
            if self.cost_subtype_id.type == 'sale' and self.sale_car_value > 0:
                # if self.vehicle_id.state_id and not self.vehicle_id.state_id.create_fleet_contract:
                #     raise ValidationError(_("Sorry you can't create sale order , please check Vehicle Status"))
                if self.sale_id:
                    raise ValidationError(_("Sorry Theres sale order created, please reset order to draft .."))

                sale_obj = self.env['sale.order'].create({
                    'partner_id': self.customer_id.id,
                    'analytic_account_id': self.vehicle_id.account_analytic_account_id.id,
                    'order_line': [(0, 0, {
                        'name': self.vehicle_id.custom_product_id.name or self.vehicle_id.name,
                        'product_id': self.vehicle_id.custom_product_id.id,
                        'price_unit': self.sale_car_value,
                        'product_uom_qty': 1.0,
                    })],
                })
                self.sale_id = sale_obj.id
            elif self.cost_subtype_id.type == 'purchase' and self.net_car_value > 0:
                if self.purchase_id:
                    raise ValidationError(_("Sorry Theres purchase order created, please reset to order draft .."))
                purchase_obj = self.env['purchase.order'].create({
                    'partner_id': self.insurer_id.id,
                    'order_line': [(0, 0, {
                        'name': self.vehicle_id.custom_product_id.name or self.vehicle_id.name,
                        'product_id': self.vehicle_id.custom_product_id.id,
                        'analytic_distribution': (self.vehicle_id.account_analytic_account_id and {
                            self.vehicle_id.account_analytic_account_id.id: 100}),
                        'price_unit': self.net_car_value,
                        'product_qty': 1.0,
                    })],
                })
                self.purchase_id = purchase_obj.id

    def create_invoice(self):
        if self.cost_subtype_id.type == 'vendor_bill':

            invoice_obj = self.env['account.move'].create({
                'move_type': 'in_invoice',
                'partner_id': self.insurer_id.id,
                'fleet_vehicle_id': self.vehicle_id.id,
                'invoice_line_ids': [(0, 0, {
                    'product_id': self.vehicle_id.custom_product_id.id,
                    'analytic_distribution': (self.vehicle_id.account_analytic_account_id and {
                        self.vehicle_id.account_analytic_account_id.id: 100}),
                    'price_unit': self.net_car_value,
                    # 'product_uom_qty': 1.0,
                    'quantity': 1.0,
                })],
            })
            self.invoice_id = invoice_obj.id
        elif self.cost_subtype_id.type == 'customer_invoice':
            invoice_obj = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': self.customer_id.id,
                'fleet_vehicle_id': self.vehicle_id.id,
                'invoice_line_ids': [(0, 0, {
                    'product_id': self.vehicle_id.custom_product_id.id,
                    'analytic_distribution': (self.vehicle_id.account_analytic_account_id and {
                        self.vehicle_id.account_analytic_account_id.id: 100}),
                    'price_unit': self.sale_car_value,
                    # 'product_uom_qty': 1.0,
                    'quantity': 1.0,
                })],
            })
            self.invoice_id = invoice_obj.id



