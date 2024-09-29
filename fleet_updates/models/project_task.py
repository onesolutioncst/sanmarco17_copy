from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"

class project_task(models.Model):
    _inherit = "project.task"

    @api.model
    def _default_user_ids(self):
        return self.env.context.keys() & {'default_personal_stage_type_ids',
                                          'default_personal_stage_type_id'} and self.env.user

    user_ids = fields.Many2many('res.users', relation='project_task_user_rel', column1='task_id', column2='user_id',
                                string='Assignees', context={'active_test': False}, tracking=True,
                                default=_default_user_ids, domain="[('active', '=', True),('id', 'not in', fleet_existing_id)]")
    fleet_user_ids = fields.Many2many(
        'res.users',
        'project_task_fleet_user_rel',
        'task_id', 'user_id',
        string='Assign Fleets',
        domain="[ ('id', 'in', fleet_existing_id)]"
    )

    fleet_existing_id = fields.Many2many('res.users', compute='_compute_fleet_existing_user_ids')
    equipment_fleet_existing_id = fields.Many2many('res.users', compute='_compute_fleet_existing_user_ids')

    def _compute_fleet_existing_user_ids(self):
        for record in self:
            fleet_employee_objs = self.env['hr.employee'].sudo().search(
                [('is_fleet', '=', True), ('employee_type', '=', 'fleet')])
            record.fleet_existing_id = fleet_employee_objs.user_id
            if 'is_equipment' in self.env['hr.employee'].sudo()._fields:
                fleet_equipment_employee_objs = self.env['hr.employee'].sudo().search(
                    ['|','|','|', ('is_fleet', '=', True), ('is_equipment','=',True), ('employee_type', '=', 'fleet'),('employee_type','=','equipment')])
                record.equipment_fleet_existing_id = fleet_equipment_employee_objs.user_id
            else:
                record.equipment_fleet_existing_id = fleet_employee_objs.user_id
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
