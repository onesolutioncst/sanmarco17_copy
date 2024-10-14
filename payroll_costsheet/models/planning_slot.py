from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging
from datetime import timedelta
_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class planning_slot(models.Model):
    _inherit = "planning.slot"

    work_entry_product_id = fields.Many2one('product.product', 'Work entry Product')