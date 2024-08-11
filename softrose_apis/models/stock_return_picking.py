from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

from odoo.exceptions import ValidationError
from . import api_global_function

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"

class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _create_returns(self):
        new_picking, pick_type_id = super(StockReturnPicking, self)._create_returns()
        picking = self.env['stock.picking'].browse(new_picking)
        picking.write({'return_picking_id': self.picking_id})
        return new_picking, pick_type_id
