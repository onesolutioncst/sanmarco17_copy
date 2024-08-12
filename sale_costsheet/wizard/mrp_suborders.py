# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.exceptions import ValidationError, UserError


class mrp_suborders(models.Model):
    _name = 'mrp.suborders'
    _description = 'Manufacture Suborders'
    mrp_manufacture_id = fields.Many2one('mrp.production', 'Costsheet')
    mrp_suborders_details_ids = fields.One2many('mrp.suborders.details', 'mrp_suborders_id', string="Details")

    def create_sub_orders(self):

        manufacutre_lines=[]
        for mrp_suborders_details_obj in self.mrp_suborders_details_ids:
            if mrp_suborders_details_obj.quantity > 0:
                if mrp_suborders_details_obj.quantity > 0 and mrp_suborders_details_obj.quantity > mrp_suborders_details_obj.remaining_qty :
                    if self.user_has_groups('sale_costsheet.group_costsheet_up_consume'):
                        manufacutre_lines.append((0, 0, {
                            'product_id': mrp_suborders_details_obj.product_id.id,
                            'product_uom_qty': mrp_suborders_details_obj.quantity
                        }))
                    else:
                        if self.mrp_manufacture_id and self.mrp_manufacture_id.analytic_distribution:
                            for analytic_id, distribution in self.mrp_manufacture_id.analytic_distribution.items():
                                project_objs =  self.env['account.analytic.account'].sudo().browse(int(analytic_id)).project_ids
                                for project_obj in project_objs:
                                    if project_obj.user_id:
                                        activity = self.env['mail.activity'].sudo().create({
                                            'summary': 'Delivery overdue to consume',
                                            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                                            'note': 'Schedule call with Admin',
                                            'res_model_id': self.env['ir.model']._get_id('mrp.production'),
                                            'res_id': self.mrp_manufacture_id.id,
                                            'user_id': project_obj.user_id.id,
                                        })
                            # raise UserError("The quantity cannot be negative!")
                            # raise ValidationError(_("Sorry Delivery Quantity is greater than remaining, Ask Project Manager"))
                else:
                    manufacutre_lines.append((0, 0, {
                        'product_id': mrp_suborders_details_obj.product_id.id,
                        'product_uom_qty': mrp_suborders_details_obj.quantity
                    }))
        if manufacutre_lines:
            next_seq = self.env['mrp.production'].sudo().search_count([('mrp_production_id','=',self.mrp_manufacture_id.id)])
            name = self.mrp_manufacture_id._get_name_backorder(self.mrp_manufacture_id.name, next_seq+1)

            manufacutre_vals = {
                'name': name,
                'origin': self.mrp_manufacture_id.name,
                'mrp_production_id': self.mrp_manufacture_id.id,
                'product_id': self.mrp_manufacture_id.product_id.id,
                'product_qty': self.mrp_manufacture_id.product_uom_qty,
                'move_raw_ids':manufacutre_lines
            }
            mrp_production_obj = self.env['mrp.production'].sudo().create(manufacutre_vals)
            mrp_production_obj.message_post_with_source(
                'mail.message_origin_link',
                render_values={'self': mrp_production_obj, 'origin': self.mrp_manufacture_id,'edit': True},
                subtype_xmlid='mail.mt_note',
            )
        # return {'type': 'ir.actions.client', 'tag': 'reload'}
        return True
class mrp_suborders_details(models.Model):
    _name = 'mrp.suborders.details'
    _description = 'Manufacture Suborders Details'

    mrp_suborders_id = fields.Many2one('mrp.suborders')
    mrp_manufacture_line_id = fields.Many2one('stock.move', 'Components')
    product_id = fields.Many2one('product.product', 'Product', domain=[('costsheet','=',True)])
    product_uom_qty = fields.Float('To Consume')
    delivery_qty = fields.Float('Delivery')
    remaining_qty = fields.Float('Remaining')
    quantity = fields.Float('Quantity')
    upconsume_qty = fields.Float('Up Consume ')