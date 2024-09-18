from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    customer_id = fields.Many2one("res.partner", "Customer", )
    type = fields.Selection("Type", related='service_type_id.type', stroe=True, )
    amount = fields.Float('Cost', compute='_compute_amount')
    sale_id = fields.Many2one("sale.order", "Sale Order")
    purchase_id = fields.Many2one("purchase.order", "Purchase Order")
    invoice_id = fields.Many2one("account.move", "Invoice")
    repair_id = fields.Many2one('repair.order', 'Repair Order')
    lines_ids = fields.One2many("fleet.vehicle.log.services.lines", "fleet_log_id", "Lines")
    fleet_owner = fields.Many2one('res.partner', string='Fleet Owner', copy=False)
    service_type_id = fields.Many2one(
        'fleet.service.type', 'Service Type', required=True) #default=lambda self: self.env.ref('fleet.type_service_service_7', raise_if_not_found=False),

    def unlink(self):
        for record in self:
            if record.state == 'done':
                raise ValidationError(_("Can't delete this record as it's in done state"))
            if record.sale_id:
                raise ValidationError(_("Can't delete this record as theres Sale order created"))
            if record.purchase_id:
                raise ValidationError(_("Can't delete this record as theres Purchase order created"))
            if record.invoice_id:
                raise ValidationError(_("Can't delete this record as theres invoice created"))
        return super(FleetVehicleLogServices, self).unlink()

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

    @api.depends('lines_ids')
    def _compute_amount(self):
        for record in self:
            if record.lines_ids:
                for line in record.lines_ids:
                    record.amount += line.price_unit * line.qty
            else:
                record.amount = 0

    def create_order(self):
        self.ensure_one()
        if not self.lines_ids:
            raise ValidationError(_("Sorry You must add lines .."))
        if self.service_type_id:
            if self.service_type_id.type == 'sale':
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
                    'analytic_account_id': self.vehicle_id.account_analytic_account_id.id,
                    'order_line': lines,
                })
                self.sale_id = sale_obj.id
            elif self.service_type_id.type == 'purchase':
                if self.purchase_id:
                    raise ValidationError(_("Sorry Theres purchase order created, please reset to order draft .."))
                lines = []
                for line in self.lines_ids:
                    lines.append((0, 0, {
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'price_unit': line.price_unit,
                        'analytic_distribution': (self.vehicle_id.account_analytic_account_id and {
                            self.vehicle_id.account_analytic_account_id.id: 100}),
                        'product_qty': line.qty,
                        'taxes_id': line.taxes_id.ids,
                    }))
                purchase_obj = self.env['purchase.order'].create({
                    'partner_id': self.vendor_id.id,
                    'order_line': lines,
                })
                self.purchase_id = purchase_obj.id

    def create_invoice(self):
        if self.service_type_id.type == 'vendor_bill':
            lines = []
            for line in self.lines_ids:
                lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'price_unit': line.price_unit,
                    'quantity': line.qty,
                    'analytic_distribution': (self.vehicle_id.account_analytic_account_id and {
                        self.vehicle_id.account_analytic_account_id.id: 100}),
                    # 'analytic_account_id': self.vehicle_id.account_analytic_account_id.id,
                    'tax_ids': line.taxes_id.ids,
                }))
            invoice_obj = self.env['account.move'].create({
                'move_type': 'in_invoice',
                'partner_id': self.vendor_id.id,
                'posted_before':True,
                'fleet_vehicle_id': self.vehicle_id.id,
                'invoice_line_ids': lines,
            })
            self.invoice_id = invoice_obj.id
        elif self.service_type_id.type == 'customer_invoice':
            lines = []
            for line in self.lines_ids:
                lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'price_unit': line.price_unit,
                    'quantity': line.qty,
                    'analytic_distribution': (self.vehicle_id.account_analytic_account_id and {
                        self.vehicle_id.account_analytic_account_id.id: 100}),
                    # 'analytic_account_id': self.vehicle_id.account_analytic_account_id.id,
                    'tax_ids': line.taxes_id.ids,
                }))
            invoice_obj = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': self.customer_id.id,
                'fleet_vehicle_id': self.vehicle_id.id,
                'invoice_line_ids': lines,
            })
            self.invoice_id = invoice_obj.id

    def get_picking_type_id(self):
        companies = self.company_id or self.env.company
        default_warehouse = self.env.user.with_company(companies.id)._get_default_warehouse_id()
        if default_warehouse and default_warehouse.repair_type_id:
            return default_warehouse.repair_type_id.id

    def create_repair(self):
        if self.service_type_id.type == 'repair':
            lines = []
            for line in self.lines_ids:
                lines.append((0, 0, {
                    'repair_line_type': line.type,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.qty,
                }))
            repair_obj = self.env['repair.order'].sudo().create({
                'partner_id': self.customer_id.id,
                'picking_type_id': self.get_picking_type_id(),
                'fleet_vehicle_id': self.vehicle_id.id,
                'move_ids': lines,
            })
            self.repair_id = repair_obj.id

class FleetVehicleLogServicesLines(models.Model):
    _name = 'fleet.vehicle.log.services.lines'

    type = fields.Selection([('add','Add'), ('remove','Remove'),('recycle','Recycle')], 'Repair Type', default="add")
    fleet_log_id = fields.Many2one("fleet.vehicle.log.services", "Service")
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
