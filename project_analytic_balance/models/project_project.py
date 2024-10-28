# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from collections import defaultdict
from logging import debug

from odoo import models, fields, api, _, _lt
from odoo.exceptions import ValidationError, RedirectWarning

class Project(models.Model):
    _inherit = "project.project"

    analytic_debit = fields.Monetary('Debit', compute="get_project_balance", currency_field='currency_id')
    analytic_credit = fields.Monetary('Credit', compute="get_project_balance", currency_field='currency_id')
    analytic_balance = fields.Monetary('Balance', compute="get_project_balance", currency_field='currency_id')


    @api.depends('analytic_account_id')
    @api.onchange('analytic_account_id')
    def get_project_balance(self):
        for record in self:
            account_move_line_objs = self.env['account.move.line'].sudo().search([('analytic_distribution','=',{str(record.analytic_account_id.id): 100})])
            account_move_line_objs = self.env['account.move.line'].sudo().search([]).filtered(lambda t: t.analytic_distribution)
            analytic_debit = 0.0
            analytic_credit = 0.0
            analytic_balance = 0.0
            for account_move_line_obj in account_move_line_objs:
                if account_move_line_obj.analytic_distribution.get(str(record.analytic_account_id.id)):
                    analytic_debit += account_move_line_obj.analytic_distribution.get(str(record.analytic_account_id.id))/100 * account_move_line_obj.debit
                    analytic_credit += account_move_line_obj.analytic_distribution.get(str(record.analytic_account_id.id)) / 100 * account_move_line_obj.credit
                    analytic_balance += account_move_line_obj.analytic_distribution.get(str(record.analytic_account_id.id)) / 100 * account_move_line_obj.balance
            record.analytic_debit  = analytic_debit
            record.analytic_credit = analytic_credit
            record.analytic_balance = analytic_balance
