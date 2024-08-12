# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.exceptions import ValidationError


class manufacture_agreement(models.TransientModel):
    _name = 'manufacture.agreement'
    _description = 'Create agreement from Manufacture costsheet'
    mrp_production_id = fields.Many2one('mrp.production')
    partner_id = fields.Many2one('res.partner', 'Vendor', domain=[('supplier_rank','=',1)])

    def create_manufacture_aggreement(self):
        purchase_requisition_vals = {}
        if self.mrp_production_id:
            mrp_production_obj = self.mrp_production_id
            purchase_requisition_vals.update({'mrp_production_id': mrp_production_obj.id,})
        else:
            mrp_production_obj = self.env['mrp.production'].browse(self._context.get('active_ids'))

        purchase_requisition = []
        origin = ''
        for mrp_production in mrp_production_obj:
            origin += mrp_production.name + ','
            if not mrp_production.mrp_production_id:
                for mrp_suborders_details_obj in mrp_production.move_raw_ids:
                    purchase_requisition.append((0, 0, {
                        'product_id': mrp_suborders_details_obj.product_id.id,
                        'product_qty': mrp_suborders_details_obj.product_uom_qty,
                        'analytic_distribution': mrp_production.analytic_distribution,
                    }))
        purchase_requisition_vals.update({
            'vendor_id': self.partner_id.id,
            'origin': origin,
            'line_ids': purchase_requisition
        })

        purchase_requisition_obj = self.env['purchase.requisition'].sudo().create(purchase_requisition_vals)
        if self.mrp_production_id:
            purchase_requisition_obj.message_post_with_source(
                'mail.message_origin_link',
                render_values={'self': purchase_requisition_obj, 'origin': self.mrp_production_id, 'edit': True},
                subtype_xmlid='mail.mt_note',
            )
        else:
            purchase_requisition_obj.message_post_with_source(
                'mail.message_origin_link',
                render_values={'self': purchase_requisition_obj, 'origin': mrp_production_obj, 'edit': True},
                subtype_xmlid='mail.mt_note',
            )
            mrp_production_obj.purchase_requisition_id = purchase_requisition_obj.id


        return True
        # return {'type': 'ir.actions.client', 'tag': 'reload'}