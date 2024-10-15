from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging
from datetime import timedelta
_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class account_analytic_line(models.Model):
    _inherit = "account.analytic.line"

    work_entry_product_id = fields.Many2one('product.product', 'Product')
    product_cost = fields.Float('Cost', related="work_entry_product_id.standard_price", store=True, readonly=False)
    total_timesheet_cost = fields.Float(compute="calc_total_timesheet_cost", string='Timesheet Cost')
    planning_slot_id = fields.Many2one('planning.slot', 'Planning')
    hr_work_entry_type_id = fields.Many2one('hr.work.entry.type', 'Work Entry Type')


    @api.onchange('work_entry_product_id')
    def onchange_work_entry_product_id(self):
        for record in self:
            record.hr_work_entry_type_id = record.work_entry_product_id.hr_work_entry_type_id.id or ''

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
