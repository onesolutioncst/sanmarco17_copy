from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"

class account_analytic_line(models.Model):
    _inherit = "account.analytic.line"

    equipment_existing_employee_id = fields.Many2many('hr.employee', compute='_compute_equipment_existing_employee_ids')

    def _compute_equipment_existing_employee_ids(self):
        for record in self:
            hr_employee_objs = self.env['hr.employee'].sudo().search([('is_equipment', '=', True), ('employee_type', '=', 'equipment')])
            record.equipment_existing_employee_id = hr_employee_objs.ids

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