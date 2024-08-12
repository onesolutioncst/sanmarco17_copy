from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"

class product_template(models.Model):
    _inherit = "product.template"

    is_equipment = fields.Boolean('Is Equipment')
    maintenance_equipment_id = fields.Many2one('maintenance.equipment', 'Equipment')



class product_product(models.Model):
    _inherit = "product.product"

    is_equipment = fields.Boolean('Is Equipment')
    maintenance_equipment_id = fields.Many2one('maintenance.equipment', 'Equipment')

    def create_equipment(self):
        if self.maintenance_equipment_id:
            self.maintenance_equipment_id.write({'name': self.name, 'product_product_id': self.id})
        else:
            maintenance_equipment_obj = self.env['maintenance.equipment'].sudo().create({'name': self.name, 'product_product_id': self.id})
            self.maintenance_equipment_id = maintenance_equipment_obj.id
        return True