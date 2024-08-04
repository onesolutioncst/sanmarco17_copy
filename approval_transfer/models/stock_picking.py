# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models,fields


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", copy=False,)
