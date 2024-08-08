from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"

class product_template(models.Model):
    _inherit = "product.template"

    is_discount = fields.Boolean('Is Discount')
    is_retention_ar = fields.Boolean('Is Retention AR')
    is_retention_ap = fields.Boolean('Is Retention AP')
    is_advanced_ar = fields.Boolean('Is Advanced AR')
    is_advanced_ap = fields.Boolean('Is Advanced AP')
    insurance = fields.Boolean('Is Insurance')
    refundable = fields.Boolean('Is Refundable')
    subcontractor = fields.Boolean('Is Subcontractor')
    variation_Order = fields.Boolean('Is Variation Order')
    wages = fields.Boolean('Is Wages')
    supplier = fields.Boolean('Is Supplier')
    customer = fields.Boolean('Is Customer')
    costsheet = fields.Boolean('Is Costsheet')
    is_fleet = fields.Boolean('Is Fleet')
    is_equipment = fields.Boolean('Is Equipment')
    maintenance_equipment_id = fields.Many2one('maintenance.equipment', 'Equipment')
    fleet_vehicle_id = fields.Many2one('fleet.vehicle', 'Fleet')


class product_product(models.Model):
    _inherit = "product.product"

    is_discount = fields.Boolean('Is Discount')
    is_retention_ar = fields.Boolean('Is Retention AR')
    is_retention_ap = fields.Boolean('Is Retention AP')
    is_advanced_ar = fields.Boolean('Is Advanced AR')
    is_advanced_ap = fields.Boolean('Is Advanced AP')
    insurance = fields.Boolean('Is Insurance')
    refundable = fields.Boolean('Is Refundable')
    subcontractor = fields.Boolean('Is Subcontractor')
    variation_Order = fields.Boolean('Is Variation Order')
    wages = fields.Boolean('Is Wages')
    supplier = fields.Boolean('Is Supplier')
    customer = fields.Boolean('Is Customer')
    costsheet = fields.Boolean('Is Costsheet')
    is_fleet = fields.Boolean('Is Fleet')
    is_equipment = fields.Boolean('Is Equipment')
    maintenance_equipment_id = fields.Many2one('maintenance.equipment', 'Equipment')
    fleet_vehicle_id = fields.Many2one('fleet.vehicle', 'Fleet')
    def create_fleet(self):
        return True

    def create_equipment(self):
        if self.maintenance_equipment_id:
            self.maintenance_equipment_id.write({'name': self.name, 'product_product_id': self.id})
        else:
            maintenance_equipment_obj = self.env['maintenance.equipment'].sudo().create({'name': self.name, 'product_product_id': self.id})
            self.maintenance_equipment_id = maintenance_equipment_obj.id

        return True