# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from collections import defaultdict
from logging import debug

from odoo import models, fields, api, _, _lt
from odoo.exceptions import ValidationError, RedirectWarning

class productTemplate(models.Model):
    _inherit = "product.template"

    product_volume = fields.Float('Cost Volume')