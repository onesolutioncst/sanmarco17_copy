# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.exceptions import ValidationError, UserError


class extra_to_consume_wizard(models.TransientModel):
    _name = 'extra.to.consume.wizard'
    _description = 'Wizard to add extra to consume qty'

    stock_move_id = fields.Many2one('stock.move', 'Component ID')
    product_id = fields.Many2one('product.product', 'Product')
    extra_qty = fields.Float('Extra Quantity')
    qty_added_datetime = fields.Datetime('Time added', default=fields.Datetime.now())

    def add_extra_toconsume_qty(self):
        self.env['extra.to.consume.history'].sudo().create({
            'mrp_manufacture_id': self.stock_move_id.raw_material_production_id.id,
            'stock_move_id': self.stock_move_id.id,
            'product_id': self.product_id.id,
            'extra_qty': self.extra_qty,
            'qty_added_datetime': self.qty_added_datetime,
        })
        self.stock_move_id.origin_qty = self.stock_move_id.origin_qty + self.extra_qty
        return {'type': 'ir.actions.act_window_close'}
