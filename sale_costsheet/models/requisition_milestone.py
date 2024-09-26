# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class purchase_requisition_milestone(models.Model):
    _name = 'purchase.requisition.milestone'

    purchase_requisition_id = fields.Many2one('purchase.requisition')
    name = fields.Char('Name')
    purchase_requisition_line_id = fields.Many2one('purchase.requisition.line', 'Requisition Item')
    quantity_percentage = fields.Float('Quantity (%)', compute="_compute_quantity_percentage", store=True,
                                       help='Percentage of the ordered quantity that will automatically be delivered once the milestone is reached.')
    product_uom_qty = fields.Float("Quantity", compute="_compute_product_uom_qty")
    deadline = fields.Date('Deadline')
    is_reached = fields.Boolean('Reached')

    @api.depends('purchase_requisition_line_id.product_qty', 'product_uom_qty')
    def _compute_quantity_percentage(self):
        for milestone in self:
            milestone.quantity_percentage = milestone.purchase_requisition_line_id.product_qty and milestone.product_uom_qty / milestone.purchase_requisition_line_id.product_qty

    @api.depends('purchase_requisition_line_id', 'quantity_percentage')
    def _compute_product_uom_qty(self):
        for milestone in self:
            if milestone.quantity_percentage:
                milestone.product_uom_qty = milestone.quantity_percentage * milestone.purchase_requisition_line_id.product_qty
            else:
                milestone.product_uom_qty = milestone.purchase_requisition_line_id.product_qty
