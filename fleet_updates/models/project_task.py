from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"

class project_task(models.Model):
    _inherit = "project.task"

    fleet_user_ids = fields.Many2many(
        'res.users',
        'project_task_fleet_user_rel',
        'task_id', 'user_id',
        string='Fleet Users',
        domain="[ ('id', 'in', fleet_existing_id)]"
    )

    fleet_existing_id = fields.Many2many('res.users', compute='_compute_fleet_existing_user_ids')

    def _compute_fleet_existing_user_ids(self):
        for record in self:
            fleet_employee_objs = self.env['hr.employee'].sudo().search(
                [('is_fleet', '=', True), ('employee_type', '=', 'fleet')])
            record.fleet_existing_id = fleet_employee_objs.user_id

    fleet_timesheet_ids = fields.One2many('account.analytic.line', 'task_id', 'Fleet Timesheets')
    allow_fleet_timesheets = fields.Boolean(
        "Allow Fleet timesheets",
        compute='_compute_allow_fleet_timesheets', search='_search_allow_fleet_timesheets',
        compute_sudo=True, readonly=True,
        help="Fleet Timesheets can be logged on this task.")

    @api.depends('project_id.allow_fleet_timesheets')
    def _compute_allow_fleet_timesheets(self):
        for task in self:
            task.allow_fleet_timesheets = task.project_id.allow_fleet_timesheets

    def _search_allow_fleet_timesheets(self, operator, value):
        query = self.env['project.project'].sudo()._search([
            ('allow_fleet_timesheets', operator, value),
        ])
        return [('project_id', 'in', query)]
