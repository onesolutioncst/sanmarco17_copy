from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class purchase_requisition(models.Model):
    _inherit = "purchase.requisition"

    mrp_production_id = fields.Many2one('mrp.production', trace=True)

class purchase_requisition_line(models.Model):
    _inherit = "purchase.requisition.line"

    remaining_qty = fields.Float(compute="calc_qty_orders", string='R A ', help="Remaining QTY")
    upconsume_qty = fields.Float(compute="calc_qty_orders", string='Up C A ', help="Up Consume QTY")

    def calc_qty_orders(self):
        for record in self:
            record.remaining_qty = 0.0
            record.upconsume_qty = 0.0
            if record.product_qty > record.qty_ordered:
                record.remaining_qty = record.product_qty - record.qty_ordered
            else:
                record.upconsume_qty = record.qty_ordered - record.product_qty