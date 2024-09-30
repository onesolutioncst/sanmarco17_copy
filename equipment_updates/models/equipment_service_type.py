from odoo import api, fields, models


class EquipmentServiceType(models.Model):
    _name = 'equipment.service.type'
    name = fields.Char(required=True, translate=True)
    category = fields.Selection([
        ('contract', 'Contract'),
        ('service', 'Service')
    ], 'Category', required=True, help='Choose whether the service refer to contracts, vehicle services or both')
    type = fields.Selection(string="Type",
                            selection=[('sale', 'Sale'), ('purchase', 'Purchase'), ('vendor_bill', 'Vendor Bill'),
                                       ('customer_invoice', 'Customer Invoice'), ('repair', 'Repair'),
                                       ('rental', 'Rental')], required=True, )
    description = fields.Text()
    user_ids = fields.Many2many('res.users', string='Access Users')
