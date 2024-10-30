# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from collections import defaultdict
from logging import debug

from odoo import models, fields, api, _, _lt
from odoo.exceptions import ValidationError, RedirectWarning

class product_product(models.Model):
    _inherit = "product.product"
    account_analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    product_volume = fields.Float('Cost Volume')

    def calc_product_volume_cost(self):
        for record in self:
            record.standard_price = 0.0
            if record.account_analytic_account_id and record.account_analytic_account_id.balance and record.product_volume > 0.0:
                record.standard_price = record.account_analytic_account_id.balance / record.product_volume

