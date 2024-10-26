# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from collections import defaultdict

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
            # self.env['account.move.line'].sudo().search([]).filtered(lambda t: t.analytic_distribution)[
            #     0].analytic_distribution
            record.analytic_debit  =sum(account_move_line_obj.debit for account_move_line_obj in account_move_line_objs)
            record.analytic_credit = sum(account_move_line_obj.credit for account_move_line_obj in account_move_line_objs)
            record.analytic_balance = sum(account_move_line_obj.balance for account_move_line_obj in account_move_line_objs)