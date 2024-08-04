from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class sale_order(models.Model):
    _inherit = "sale.order"

    is_costsheet = fields.Boolean('Costsheet')
    costsheet_count = fields.Integer('costsheet count', compute="calc_costsheet_count")
    def create_sale_costsheet(self):
        for record in self:
            for sale_line_obj in record.order_line:
                if sale_line_obj.mrp_production_costsheet_id:
                    sale_line_obj.mrp_production_costsheet_id.write({'product_id': sale_line_obj.product_id.id,
                                                                     'product_qty': sale_line_obj.product_uom_qty})
                else:
                    mrp_production_costsheet_obj = sale_line_obj.mrp_production_costsheet_id.create({
                        'product_id': sale_line_obj.product_id.id,
                        'product_qty': sale_line_obj.product_uom_qty,
                        'sale_costsheet_id': record.id,
                        'sale_line_costsheet_id': sale_line_obj.id
                    })
                    sale_line_obj.mrp_production_costsheet_id = mrp_production_costsheet_obj.id
        return True

    def action_view_costsheet(self):
        action = self.env['ir.actions.actions']._for_xml_id('sale_costsheet.mrp_production_costsheet_action')
        mrp_costsheet_ids = self.order_line.mapped('mrp_production_costsheet_id').ids
        action['domain'] = [('id', 'in', mrp_costsheet_ids)]
        return action

    def calc_costsheet_count(self):
        self.costsheet_count = len(self.order_line.mapped('mrp_production_costsheet_id'))
class sale_order_line(models.Model):
    _inherit = "sale.order.line"

    mrp_production_costsheet_id = fields.Many2one('mrp.production')