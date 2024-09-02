from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging
from datetime import datetime, timedelta
_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class stock_warehouse(models.Model):
    _inherit = "stock.warehouse"

    code = fields.Char('Code', size=10)


