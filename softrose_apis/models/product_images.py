from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging
from . import api_global_function

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class product_images(models.Model):
    _name = "product.images"

    product_id = fields.Many2one('product.template', 'Product')
    image_link = fields.Char('Image Link')



