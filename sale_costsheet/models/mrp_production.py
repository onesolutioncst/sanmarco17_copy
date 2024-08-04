from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class mrp_production(models.Model):
    _inherit = "mrp.production"

    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=[],
        compute='_compute_product_id', store=True, copy=True, precompute=True,
        readonly=False, required=True, check_company=True)

    is_costsheet = fields.Boolean('Costsheet')
    sale_costsheet_id = fields.Many2one('sale.order')
    sale_line_costsheet_id = fields.Many2one('sale.order.line')
    suborder_count = fields.Integer(compute="calc_suborder_count")
    mrp_production_id = fields.Many2one('mrp.production')

    @api.onchange('is_costsheet')
    def check_onchange_is_costsheet(self):
        for record in self:
            if not record.is_costsheet:
                return {'domain':{'product_id':[('type', 'in', ['product', 'consu'])]}}

    def action_view_suborder(self):
        return {
            'name': _('Costsheet Sub Orders'),
            'view_mode': 'tree,form',
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('mrp_production_id','=',self.id)],
            'context':{'default_mrp_production_id': self.id, 'default_product_id': self.product_id.id}
        }

    def calc_suborder_count(self):
        for record in self:
            record.suborder_count = self.search_count([('mrp_production_id','=',record.id)])

    def action_create_suborder(self):
        self.ensure_one()
        wizard_mrp_suborders = []
        for move_raw_obj in self.move_raw_ids:
            wizard_mrp_suborder_id = self.env['mrp.suborders.details'].create({
                'mrp_manufacture_line_id': move_raw_obj.id,
                'product_id': move_raw_obj.product_id.id,
                'product_uom_qty': move_raw_obj.product_uom_qty,
                'quantity': move_raw_obj.quantity,

            })
            wizard_mrp_suborders.append(wizard_mrp_suborder_id.id)
        if wizard_mrp_suborders:
            new_wizard = self.env['mrp.suborders'].create({
                'mrp_manufacture_id': self.id,
                'mrp_suborders_details_ids': [(6, 0, wizard_mrp_suborders)],
            })
        return {
            'name': _('Costsheet Sub Orders'),
            'view_mode': 'form',
            'res_model': 'mrp.suborders',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': new_wizard.id,
        }


class stock_move(models.Model):
    _inherit = "stock.move"

    qty_orders = fields.Float(compute="calc_qty_orders", string='Sub orders QTY')

    def calc_qty_orders(self):
        for record in self:
            qty_orders = 0.0
            mrp_suborders_objs = self.env['mrp.production'].sudo().search([('mrp_production_id','=',record.raw_material_production_id.id)])
            for mrp_suborders_obj in mrp_suborders_objs:
                for move_raw_obj in mrp_suborders_obj.move_raw_ids:
                    if move_raw_obj.product_id == record.product_id:
                        qty_orders += move_raw_obj.product_qty
                record.qty_orders = qty_orders
            # record.quantity = qty_orders

