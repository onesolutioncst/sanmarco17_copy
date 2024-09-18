# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models, Command
from odoo.exceptions import UserError

class purchaseagreementlinkalternative(models.TransientModel):
    _name = 'purchase.agreement.link.alternative'
    _description = 'Wizard to link alternative PR'

    origin_po_id = fields.Many2one(
        'purchase.requisition', help="The original PR that this alternative PR is being created for."
    )

    purchase_requisition_ids = fields.Many2many('purchase.requisition', string='Purchase Agreement')

    def action_link_alternative(self):
        self.purchase_requisition_ids.purchase_requisition_id = self.origin_po_id.id

        # alt_po.order_line._compute_tax_id()
        return {'type': 'ir.actions.act_window_close'}