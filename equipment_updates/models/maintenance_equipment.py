from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class maintenance_equipment(models.Model):
    _inherit = "maintenance.equipment"

    is_product = fields.Boolean('Is Product')
    product_product_id = fields.Many2one('product.product', 'Product')
    is_employee = fields.Boolean('Is Timesheet')
    hr_employee_id= fields.Many2one('hr.employee', 'Employee')

    def create_equipment_product(self):
        if self.product_product_id:
            self.product_product_id.write(
                {'name': self.name, 'is_equipment': True, 'maintenance_equipment_id': self.id})
        else:
            product_product_obj = self.env['product.product'].sudo().create(
                {'name': self.name, 'is_equipment': True, 'maintenance_equipment_id': self.id})
            self.product_product_id = product_product_obj.id

        return True
    def create_equipment_employee(self):
        if self.hr_employee_id:
            self.hr_employee_id.write(
                {'name': self.name, 'is_equipment': True, 'employee_equipment_id': self.id,
                 'employee_type': 'equipment'})
        else:
            hr_employee_obj = self.env['hr.employee'].sudo().create(
                {'name': self.name, 'is_equipment': True, 'employee_equipment_id': self.id,
                 'employee_type': 'equipment'})
            self.hr_employee_id = hr_employee_obj.id
        return True
