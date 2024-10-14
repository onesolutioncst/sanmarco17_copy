from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging
from datetime import timedelta, datetime
_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class account_analytic_line(models.Model):
    _inherit = "account.analytic.line"

    fleet_existing_employee_id = fields.Many2many('hr.employee', compute='_compute_fleet_existing_employee_ids')
    fleet_equipment_existing_employee_id = fields.Many2many('hr.employee',
                                                            compute='_compute_fleet_equipment_existing_employee_ids')

    @api.onchange('date')
    def _compute_fleet_equipment_existing_employee_ids(self):
        for record in self:
            domain = [('is_fleet', '=', True), ('employee_type', '=', 'fleet')]
            if 'is_equipment' in self.env['hr.employee'].sudo()._fields:
                domain = ['|','|',('is_fleet', '=', True),('is_equipment', '=', True), ('employee_type', 'in', ['fleet','equipment'])]
            hr_employee_objs = self.env['hr.employee'].sudo().search(domain)
            record.fleet_equipment_existing_employee_id = hr_employee_objs.ids

    def _compute_fleet_existing_employee_ids(self):
        for record in self:
            hr_employee_objs = self.env['hr.employee'].sudo().search(
                [('is_fleet', '=', True), ('employee_type', '=', 'fleet')])
            record.fleet_existing_employee_id = hr_employee_objs.ids

    @api.model
    def default_get(self, field_list):
        result = super(account_analytic_line, self).default_get(field_list)
        result['employee_id'] = ''
        if not self._context.get('default_project_id') and self._context.get('is_timesheet'):
            employee_id = result.get('employee_id', self.env.context.get('default_employee_id', False))
            favorite_project_id = self._get_favorite_project_id(employee_id)
            if favorite_project_id:
                result['project_id'] = favorite_project_id
        return result

    work_entry_product_id = fields.Many2one('product.product', 'Work entry Product')
    product_cost = fields.Float('Cost', related="work_entry_product_id.standard_price", store=True, readonly=False)
    total_timesheet_cost = fields.Float(compute="calc_total_timesheet_cost", string='Timesheet Cost')
    planning_slot_id = fields.Many2one('planning.slot', 'Planning')

    @api.onchange('product_cost', 'work_entry_product_id', 'unit_amount')
    @api.depends('product_cost', 'work_entry_product_id', 'unit_amount')
    def calc_total_timesheet_cost(self):
        for record in self:
            record.total_timesheet_cost = record.product_cost * record.unit_amount

    def create_timesheet_plan(self):
        for record in self:
            hours = int(record.unit_amount)  # Get the whole number of hours
            minutes = round((record.unit_amount - hours) * 60)  # Convert the fractional part to minutes
            planning_dict = {
                'start_datetime': record.date,
                'end_datetime': record.date + timedelta(hours=hours, minutes=minutes),
                'resource_id': record.employee_id.resource_id.id,
                'work_entry_product_id': record.work_entry_product_id.id
            }
            if record.planning_slot_id:
                record.planning_slot_id.write(planning_dict)
            else:
                record.planning_slot_id.create(planning_dict)
            return True

