from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"

class product_template(models.Model):
    _inherit = "product.template"

    is_fleet = fields.Boolean('Is Fleet')
    fleet_vehicle_id = fields.Many2one('fleet.vehicle', 'Fleet')



class product_product(models.Model):
    _inherit = "product.product"

    is_fleet = fields.Boolean('Is Fleet')
    fleet_vehicle_id = fields.Many2one('fleet.vehicle', 'Fleet')


    def create_fleet(self):
        if self.fleet_vehicle_id:
            self.fleet_vehicle_id.write({'name': self.name, 'product_product_id': self.id})
        else:
            fleet_vehicle_obj = self.env['fleet.vehicle'].sudo().create({'name': self.name, 'product_product_id': self.id})
            self.fleet_vehicle_id = fleet_vehicle_obj.id
        return True