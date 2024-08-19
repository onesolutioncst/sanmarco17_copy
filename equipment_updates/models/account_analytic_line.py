from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"

class account_analytic_line(models.Model):
    _inherit = "account.analytic.line"

    equipment_existing_employee_id = fields.Many2many('res.users', compute='_compute_equipment_existing_employee_ids')

    def _compute_equipment_existing_employee_ids(self):
        for record in self:
            record.equipment_existing_id = self.env['hr.employee'].sudo().search([('is_equipment','=',True), ('employee_type','=','equipment')])
