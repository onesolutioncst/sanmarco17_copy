from ast import literal_eval
from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"

class fleet_vehicle(models.Model):
    _inherit = "fleet.vehicle"

    is_product = fields.Boolean('Is Product')
    product_product_id = fields.Many2one('product.product', 'Product')
    is_employee = fields.Boolean('Is Timesheet')
    hr_employee_id = fields.Many2one('hr.employee', 'Employee')
    has_timesheet = fields.Boolean(compute='_compute_has_timesheet')

    def _compute_has_timesheet(self):
        self.env.cr.execute("""
                SELECT id, EXISTS(SELECT 1 FROM account_analytic_line WHERE project_id IS NOT NULL AND employee_id = e.id limit 1)
                  FROM hr_employee e
                 WHERE id in %s
                """, (tuple(self.ids),))

        result = {eid[0]: eid[1] for eid in self.env.cr.fetchall()}

        for employee in self:
            employee.has_timesheet = result.get(employee.id, False)

    def create_fleet_product(self):
        if self.product_product_id:
            self.product_product_id.write({'name': self.name, 'is_fleet': True, 'fleet_vehicle_id': self.id})
        else:
            product_product_obj = self.env['product.product'].sudo().create({'name': self.name, 'is_fleet': True, 'fleet_vehicle_id': self.id})
            self.product_product_id = product_product_obj.id
        return True

    def create_fleet_employee(self):
        if self.hr_employee_id:
            self.hr_employee_id.write(
                {'name': self.name, 'is_fleet': True, 'employee_fleet_id': self.id,
                 'employee_type': 'fleet'})
        else:
            hr_employee_obj = self.env['hr.employee'].sudo().create(
                {'name': self.name, 'is_fleet': True, 'employee_fleet_id': self.id,
                 'employee_type': 'fleet'})
            self.hr_employee_id = hr_employee_obj.id
        return True

    def action_timesheet_from_employee(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("hr_timesheet.timesheet_action_from_employee")
        context = literal_eval(action['context'].replace('active_id', str(self.id)))
        context['create'] = context.get('create', True) and self.active
        context['domain'] = [('project_id', '!=', False), ('employee_id', '=', self.hr_employee_id.id)]
        context['grid_range'] = "week"
        action['context'] = context
        return action
