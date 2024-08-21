from odoo import api, fields, models


class FleetServiceType(models.Model):
    _inherit = 'fleet.service.type'
    type = fields.Selection(string="Type",
                            selection=[('sale', 'Sale'), ('purchase', 'Purchase'), ('vendor_bill', 'Vendor Bill'),
                                       ('customer_invoice', 'Customer Invoice')], required=True, )
    user_ids = fields.Many2many('res.users', string='Access Users')