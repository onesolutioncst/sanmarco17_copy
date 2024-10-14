from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging
_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class hr_work_entry_type(models.Model):
    _inherit = "hr.work.entry.type"

    product_id = fields.Many2one('product.product')
