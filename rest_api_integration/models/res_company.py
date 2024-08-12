from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging
from . import api_global_function
_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"

class res_company(models.Model):
    _inherit = "res.company"

    around_area = fields.Float('Around Area', default=50.0)
    app_name = fields.Char("App Name")
    app_version = fields.Char("App Version")
    app_store_app_link = fields.Char("App Store URL")
    google_play_app_link = fields.Char("App Google Play URL")
