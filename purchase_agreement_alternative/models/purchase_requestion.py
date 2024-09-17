# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, time

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    alternative_pr_ids = fields.One2many(
        'purchase.requisition', 'purchase_requisition_id',
        string="Alternative PR", check_company=True,
        help="Other potential purchase agreement for requestion products")

    #        domain="[('id', '!=', id), ('state', 'in', ['draft', 'sent', 'to approve'])]",

    purchase_requisition_id = fields.Many2one('purchase.requisition')

    def action_create_alternative(self):
        ctx = dict(**self.env.context, default_origin_po_id=self.id)
        return {
            'name': _('Create Agreement Alternative'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.agreement.create.alternative',
            'view_id': self.env.ref('purchase_agreement_alternative.purchase_agreement_create_alternative_form').id,
            'target': 'new',
            'context': ctx,
        }

    def action_compare_alternative_lines(self):
        ctx = dict(
            self.env.context,
            search_default_groupby_product=True,
            purchase_requisition_id=self.id,
        )
        view_id = self.env.ref('purchase_agreement_alternative.purchase_requestion_order_line_compare_tree').id
        return {
            'name': _('Compare Order Lines'),
            'type': 'ir.actions.act_window',
            'view_mode': 'list',
            'res_model': 'purchase.requisition.line',
            'views': [(view_id, "list")],
            'domain': [('requisition_id', 'in', (self | self.alternative_pr_ids).ids)],
            'context': ctx,
        }



class PurchaseRequisitionline(models.Model):
    _inherit = "purchase.requisition.line"

    currency_id = fields.Many2one(string='res.currency', related="requisition_id.currency_id")
    state = fields.Selection('State', related="requisition_id.state")
    vendor_id = fields.Many2one('res.partner', related="requisition_id.vendor_id")