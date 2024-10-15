from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging
_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class product_product(models.Model):
    _inherit = "product.product"

    hr_work_entry_type_id = fields.Many2one('hr.work.entry.type')