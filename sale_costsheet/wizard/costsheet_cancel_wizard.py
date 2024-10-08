# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.exceptions import ValidationError, UserError


class costsheet_cancel_wizard(models.TransientModel):
    _name = 'costsheet.cancel.wizard'
    _description = 'Cancel Manufacture Suborders'
    mrp_manufacture_id = fields.Many2one('mrp.production', 'Costsheet')

    def cancel_manufacture_costsheet(self):
        for move_raw_objs in self.mrp_manufacture_id.move_raw_ids:
            if self.mrp_manufacture_id.mrp_production_id:
                for main_move_raw_objs in self.mrp_manufacture_id.mrp_production_id.move_raw_ids:
                    if main_move_raw_objs == move_raw_objs.main_stock_move_id:
                        move_raw_objs.main_stock_move_id.product_uom_qty = move_raw_objs.main_stock_move_id.product_uom_qty +  move_raw_objs.product_uom_qty

        return True

