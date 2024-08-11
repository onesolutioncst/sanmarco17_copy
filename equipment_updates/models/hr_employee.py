from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class hr_employee(models.Model):
    _inherit = "hr.employee"

    is_equipment = fields.Boolean('Is Equipment')
    employee_equipment_id = fields.Many2one('maintenance.equipment', 'Equipment')
    employee_type = fields.Selection(selection_add=[('equipment', 'Equipment')],ondelete={'equipment': 'cascade'})

    def create_equipment(self):
        if self.employee_equipment_id:
            self.employee_equipment_id.write({'name': self.name, 'hr_employee_id': self.id,'is_employee': True})
        else:
            employee_equipment_obj = self.env['maintenance.equipment'].sudo().create(
                {'name': self.name, 'hr_employee_id': self.id,'is_employee': True})
            self.employee_equipment_id = employee_equipment_obj.id
        return True
