# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.exceptions import ValidationError


class approval_costsheet_wizard(models.TransientModel):
    _name = 'approval.costsheet.wizard'
    _description = 'Approval Costsheet Wizard'

    mrp_manufacture_id = fields.Many2one('mrp.production', 'Costsheet')
    approval_type = fields.Selection(
        [('costsheet_suborder', 'CostSheet (Suborder)'), ('costsheet_agreement', 'Costsheet (Agreement)')], )
    vendor_id = fields.Many2one('res.partner', 'Vendor ')

    def create_costsheet_approval(self):
        if self.approval_type == 'costsheet_suborder':
            product_line_list = []
            for mrp_suborders_details_obj in self.mrp_manufacture_id.move_raw_ids:
                product_line_list.append((0, 0, {
                    'product_id': mrp_suborders_details_obj.product_id.id,
                    'quantity': mrp_suborders_details_obj.remaining_qty,
                    'mrp_manufacture_line_id': mrp_suborders_details_obj.id,
                }))
            approval_request_dict = {
                'name': self.mrp_manufacture_id.name,
                'mrp_production_id': self.mrp_manufacture_id.id,
                'category_id': self.env.ref(
                    'approval_costsheet.approval_category_data_suborder').id,
                'date_start': fields.Datetime.now(),
                'date_end': fields.Datetime.now(),
                'location': 'testland',
                'picking_type_id': self.mrp_manufacture_id.picking_type_id.id,
                'location_src_id': self.mrp_manufacture_id.location_src_id.id,
                'location_dest_id': self.mrp_manufacture_id.location_dest_id.id,
                'from_mrp': True,
                'product_line_ids': product_line_list}

            approval_request_obj = self.env['approval.request'].create(approval_request_dict)
        if self.approval_type == 'costsheet_agreement':
            purchase_requisition = []
            for mrp_suborders_details_obj in self.mrp_manufacture_id.move_raw_ids:
                purchase_requisition.append((0, 0, {
                    'product_id': mrp_suborders_details_obj.product_id.id,
                    'quantity': mrp_suborders_details_obj.remaining_qty,
                    'mrp_manufacture_line_id': mrp_suborders_details_obj.id,
                }))
            approval_request_agreement_dict = {
                'name': self.mrp_manufacture_id.name,
                'mrp_production_id': self.mrp_manufacture_id.id,
                'category_id': self.env.ref('approval_costsheet.approval_category_data_agreement').id,
                'date_start': fields.Datetime.now(),
                'date_end': fields.Datetime.now(),
                'vendor_id': self.vendor_id.id,
                'product_line_ids': purchase_requisition
            }
            approval_request_obj = self.env['approval.request'].create(approval_request_agreement_dict)
        return True
