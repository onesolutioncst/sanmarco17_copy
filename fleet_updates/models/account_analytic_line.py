from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"

class account_analytic_line(models.Model):
    _inherit = "account.analytic.line"

    fleet_existing_employee_id = fields.Many2many('res.users', compute='_compute_fleet_existing_employee_ids')

    def _compute_fleet_existing_employee_ids(self):
        for record in self:
            record.fleet_existing_id = self.env['hr.employee'].sudo().search([('is_fleet','=',True), ('employee_type','=','fleet')])
