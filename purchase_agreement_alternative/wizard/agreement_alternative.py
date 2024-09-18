# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models, Command
from odoo.exceptions import UserError

class purchaseagreementcreatealternative(models.TransientModel):
    _name = 'purchase.agreement.create.alternative'
    _description = 'Wizard to preset values for alternative PO'

    origin_po_id = fields.Many2one(
        'purchase.requisition', help="The original PR that this alternative PR is being created for."
    )
    vendor_id = fields.Many2one(
        'res.partner', string='Vendor', required=True,
        help="Choose a vendor for alternative PR")
    copy_products = fields.Boolean(
        "Copy Products", default=True,
        help="If this is checked, the product quantities of the original PO will be copied")

    def action_create_alternative(self):
        # if self.env.user.has_group('purchase.group_warning_purchase') and self.creation_blocked:
        #     raise UserError(
        #         _('The vendor you have selected or at least one of the products you are copying from the original '
        #           'order has a blocking warning on it and cannot be selected to create an alternative.')
        #     )
        vals = self._get_alternative_values()
        alt_po = self.env['purchase.requisition'].with_context(origin_po_id=self.origin_po_id.id, default_requisition_id=False).create(vals)
        # alt_po.order_line._compute_tax_id()
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.requisition',
            'res_id': alt_po.id,
            'context': {
                'active_id': alt_po.id,
            },
        }

    def _get_alternative_values(self):
        vals = {
            'ordering_date': self.origin_po_id.ordering_date,
            'vendor_id': self.vendor_id.id,
            'user_id': self.origin_po_id.user_id.id,
            'type_id': self.origin_po_id.type_id.id,
            'currency_id': self.origin_po_id.currency_id.id,
            'date_end': self.origin_po_id.date_end,
            'schedule_date': self.origin_po_id.schedule_date,
            'origin': self.origin_po_id.name,
            'picking_type_id': self.origin_po_id.picking_type_id.id,
            'purchase_requisition_id': self.origin_po_id.id
        }
        if self.copy_products and self.origin_po_id:
            vals['line_ids'] = [Command.create(self._get_alternative_line_value(line)) for line in self.origin_po_id.line_ids]
        return vals

    @api.model
    def _get_alternative_line_value(self, order_line):
        return {
            'product_id': order_line.product_id.id,
            'product_description_variants': order_line.product_description_variants,
            'product_qty': order_line.product_qty,
            'analytic_distribution': order_line.analytic_distribution,
            'price_unit': order_line.price_unit,
        }


