from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class hr_employee(models.Model):
    _inherit = "hr.employee"

    is_fleet = fields.Boolean('Is Fleet')
    employee_fleet_id = fields.Many2one('fleet.vehicle', 'Fleet')
    employee_type = fields.Selection(selection_add=[('fleet', 'Fleet')],ondelete={'fleet': 'cascade'})

    def create_fleet(self):
        if self.employee_fleet_id:
            self.employee_fleet_id.write({'name': self.name, 'hr_employee_id': self.id,'is_employee': True})
        else:
            employee_fleet_obj = self.env['fleet.vehicle'].sudo().create(
                {'name': self.name, 'hr_employee_id': self.id,'is_employee': True})
            self.employee_fleet_id = employee_fleet_obj.id
        return True
