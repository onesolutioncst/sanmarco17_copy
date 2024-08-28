from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class equipmentvehiclelogcontract(models.Model):
    _name = 'equipment.vehicle.log.contract'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'name'

    active = fields.Boolean(default=True)
    maintenance_equipment_id = fields.Many2one('maintenance.equipment', 'Equipment', required=True)
    cost_subtype_id = fields.Many2one('fleet.service.type', 'Type', help='Cost type purchased with this cost',
                                      domain=[('category', '=', 'contract')])
    type = fields.Selection("Type", related='cost_subtype_id.type', stroe=True, )
    amount = fields.Monetary('Cost', tracking=True)
    date = fields.Date(help='Date when the cost has been executed')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    name = fields.Char(string='Name', compute='_compute_contract_name', store=True, readonly=False)
    active = fields.Boolean(default=True)
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user, index=True)
    start_date = fields.Date(
        'Contract Start Date', default=fields.Date.context_today,
        help='Date when the coverage of the contract begins')
    expiration_date = fields.Date(
        'Contract Expiration Date', default=lambda self:
        self.compute_next_year_date(fields.Date.context_today(self)),
        help='Date when the coverage of the contract expirates (by default, one year after begin date)')
    days_left = fields.Integer(compute='_compute_days_left', string='Warning Date')
    expires_today = fields.Boolean(compute='_compute_days_left')
    insurer_id = fields.Many2one('res.partner', 'Vendor')
    ins_ref = fields.Char('Reference', size=64, copy=False)
    state = fields.Selection([
        ('new', 'New'),
        ('running', 'Running'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='new', string='Stage', group_expand='_expand_states', tracking=True)
    sale_id = fields.Many2one("sale.order", "Sale Order")
    purchase_id = fields.Many2one("purchase.order", "Purchase Order")
    invoice_id = fields.Many2one("account.move", "Invoice")
    notes = fields.Html('Terms and Conditions', copy=False)
    cost_generated = fields.Monetary('Recurring Cost', tracking=True)
    cost_frequency = fields.Selection([
        ('no', 'No'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly')
    ], 'Recurring Cost Frequency', default='monthly', required=True)
    sale_car_value = fields.Float(string='Sales Value')
    net_car_value = fields.Float(string='Purchase Value')
    customer_id = fields.Many2one("res.partner", "Customer", )
    lines_ids = fields.One2many("equipment.vehicle.log.contract.lines", "equipment_log_id", "Lines")

    @api.depends('lines_ids')
    def _compute_amount(self):
        for record in self:
            if record.lines_ids:
                for line in record.lines_ids:
                    record.amount += line.price_unit * line.qty
            else:
                record.amount = 0

    def compute_next_year_date(self, strdate):
        oneyear = relativedelta(years=1)
        start_date = fields.Date.from_string(strdate)
        return fields.Date.to_string(start_date + oneyear)


    @api.depends('expiration_date', 'state')
    def _compute_days_left(self):
        """return a dict with as value for each contract an integer
        if contract is in an open state and is overdue, return 0
        if contract is in a closed state, return -1
        otherwise return the number of days before the contract expires
        """
        today = fields.Date.from_string(fields.Date.today())
        for record in self:
            if record.expiration_date and record.state in ['open', 'expired']:
                renew_date = fields.Date.from_string(record.expiration_date)
                diff_time = (renew_date - today).days
                record.days_left = diff_time if diff_time > 0 else 0
                record.expires_today = diff_time == 0
            else:
                record.days_left = -1
                record.expires_today = False

    @api.depends('maintenance_equipment_id.name', 'cost_subtype_id')
    def _compute_contract_name(self):
        for record in self:
            name = record.maintenance_equipment_id.name
            if name and record.cost_subtype_id.name:
                name = record.cost_subtype_id.name + ' ' + name
            record.name = name

    def unlink(self):
        for record in self:
            if record.sale_id or record.purchase_id or record.invoice_id:
                raise ValidationError(_("Sorry you can't delete this contract as theres Order/Invoice on it "))
        return super(equipmentvehiclelogcontract, self).unlink()

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
        return super(equipmentvehiclelogcontract, self).unlink()

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

    def create_order(self):
        self.ensure_one()
        if not self.lines_ids:
            raise ValidationError(_("Sorry You must add lines .."))
        if self.cost_subtype_id:
            if self.cost_subtype_id.type == 'sale':
                if self.sale_id:
                    raise ValidationError(_("Sorry Theres sale order created, please reset order to draft .."))
                lines = []
                for line in self.lines_ids:
                    lines.append((0, 0, {
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'price_unit': line.price_unit,
                        'product_uom_qty': line.qty,
                        'tax_id': line.taxes_id.ids,
                    }))
                sale_obj = self.env['sale.order'].create({
                    'partner_id': self.customer_id.id,
                    'maintenance_equipment_id': self.maintenance_equipment_id.id,
                    'order_line': lines,
                })
                self.sale_id = sale_obj.id
            elif self.cost_subtype_id.type == 'purchase':
                if self.purchase_id:
                    raise ValidationError(_("Sorry Theres purchase order created, please reset to order draft .."))
                lines = []
                for line in self.lines_ids:
                    lines.append((0, 0, {
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'price_unit': line.price_unit,
                        'product_qty': line.qty,
                        'taxes_id': line.taxes_id.ids,
                    }))
                purchase_obj = self.env['purchase.order'].create({
                    'partner_id': self.vendor_id.id,
                    'maintenance_equipment_id': self.maintenance_equipment_id.id,
                    'order_line': lines,
                })
                self.purchase_id = purchase_obj.id

    def create_invoice(self):
        if self.cost_subtype_id.type == 'vendor_bill':

            invoice_obj = self.env['account.move'].create({
                'move_type': 'in_invoice',
                'partner_id': self.insurer_id.id,
                'maintenance_equipment_id': self.maintenance_equipment_id.id,
                'invoice_line_ids': [(0, 0, {
                    'product_id': self.maintenance_equipment_id.product_product_id.id,
                    'price_unit': self.net_car_value,
                    'quantity': 1.0,
                })],
            })
            self.invoice_id = invoice_obj.id
        elif self.cost_subtype_id.type == 'customer_invoice':
            invoice_obj = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': self.customer_id.id,
                'maintenance_equipment_id': self.maintenance_equipment_id.id,
                'invoice_line_ids': [(0, 0, {
                    'product_id': self.maintenance_equipment_id.product_product_id.id,
                    'price_unit': self.sale_car_value,
                    'quantity': 1.0,
                })],
            })
            self.invoice_id = invoice_obj.id


class equipmentVehicleLogServicesLines(models.Model):
    _name = 'equipment.vehicle.log.contract.lines'

    type = fields.Selection([('add','Add'), ('remove','Remove'),('recycle','Recycle')], 'Repair Type', default="add")
    equipment_log_id = fields.Many2one("equipment.vehicle.log.contract", "Contract")
    product_id = fields.Many2one("product.product", "Product", )
    name = fields.Char('Description')
    price_unit = fields.Float("Price Unit")
    qty = fields.Float("Qty")
    taxes_id = fields.Many2many("account.tax", string="Taxes")

    @api.onchange('product_id')
    def onchange_product_id(self):
        for record in self:
            # record.name = record.product_id.name if record.product_id else '' # by manea
            record.qty = 1
            record.price_unit = record.product_id.list_price if record.product_id else 0.0



