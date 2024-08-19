# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from collections import defaultdict

from odoo import models, fields, api, _, _lt
from odoo.exceptions import ValidationError, RedirectWarning

class Project(models.Model):
    _inherit = "project.project"

    allow_equipment_timesheets = fields.Boolean(
        "Timesheets", compute='_compute_allow_timesheets', store=True, readonly=False,
        default=True)

    @api.depends('analytic_account_id')
    def _compute_allow_timesheets(self):
        without_account = self.filtered(lambda t: not t.analytic_account_id and t._origin)
        without_account.update({'allow_equipment_timesheets': False})
