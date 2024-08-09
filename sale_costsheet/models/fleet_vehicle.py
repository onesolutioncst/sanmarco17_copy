from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"

class fleet_vehicle(models.Model):
    _inherit = "fleet.vehicle"

    is_product = fields.Boolean('Is Product')
    product_product_id = fields.Many2one('product.product', 'Product')

    def create_fleet_product(self):
        if self.product_product_id:
            self.product_product_id.write({'name': self.name, 'is_fleet': True, 'fleet_vehicle_id': self.id})
        else:
            product_product_obj = self.env['product.product'].sudo().create({'name': self.name, 'is_fleet': True, 'fleet_vehicle_id': self.id})
            self.product_product_id = product_product_obj.id
        return True