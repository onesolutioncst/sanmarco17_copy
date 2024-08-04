# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class mrp_suborders(models.TransientModel):
    _name = 'mrp.suborders'
    _description = 'Manufacture Suborders'
    mrp_manufacture_id = fields.Many2one('mrp.production', 'Costsheet')
    mrp_suborders_details_ids = fields.Many2many('mrp.suborders.details', string="Details")

    def create_sub_orders(self):

        manufacutre_lines=[]
        for mrp_suborders_details_obj in self.mrp_suborders_details_ids:
            manufacutre_lines.append((0, 0, {
                'product_id': mrp_suborders_details_obj.product_id.id,
                'product_uom_qty': mrp_suborders_details_obj.quantity
            }))
        manufacutre_vals = {
            'mrp_production_id': self.mrp_manufacture_id.id,
            'product_id': self.mrp_manufacture_id.product_id.id,
            'product_qty': self.mrp_manufacture_id.product_uom_qty,
            'move_raw_ids':manufacutre_lines
        }

        mrp_production_obj = self.env['mrp.production'].sudo().create(manufacutre_vals)
        return True
class mrp_suborders_details(models.Model):
    _name = 'mrp.suborders.details'
    _description = 'Manufacture Suborders Details'

    mrp_manufacture_line_id = fields.Many2one('stock.move', 'Components')
    product_id = fields.Many2one('product.product', 'Product')
    product_uom_qty = fields.Float('To Consume')
    quantity = fields.Float('Quantity')