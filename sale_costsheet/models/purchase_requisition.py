from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class purchase_requisition(models.Model):
    _inherit = "purchase.requisition"

    mrp_production_id = fields.Many2one('mrp.production', trace=True)



