from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"

class project_task(models.Model):
    _inherit = "project.task"

    equipment_user_ids = fields.Many2many(
        'res.users',
        'project_task_equipment_user_rel',
        'task_id', 'user_id',
        string='Equipment Users',
        domain="[ ('id', 'in', equipment_existing_id)]"
    )
    equipment_existing_id = fields.Many2many('res.users', compute='_compute_equipment_existing_user_ids')
    equipment_timesheet_ids = fields.One2many('account.analytic.line', 'task_id', 'Equipment Timesheets')
    allow_equipment_timesheets = fields.Boolean(
        "Allow Equipment timesheets",
        compute='_compute_allow_equipment_timesheets', search='_search_allow_equipment_timesheets',
        compute_sudo=True, readonly=True,
        help="Equipment Timesheets can be logged on this task.")

    def _compute_equipment_existing_user_ids(self):
        for record in self:
            equipment_employee_objs = self.env['hr.employee'].sudo().search([('is_equipment','=',True), ('employee_type','=','equipment')])
            record.equipment_existing_id = equipment_employee_objs.user_id

    @api.depends('project_id.allow_equipment_timesheets')
    def _compute_allow_equipment_timesheets(self):
        for task in self:
            task.allow_equipment_timesheets = task.project_id.allow_equipment_timesheets

    def _search_allow_equipment_timesheets(self, operator, value):
        query = self.env['project.project'].sudo()._search([
            ('allow_equipment_timesheets', operator, value),
        ])
        return [('project_id', 'in', query)]
