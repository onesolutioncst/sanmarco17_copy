# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, time

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PurchaseRequisitionGroup(models.Model):
    _name = 'purchase.requisition.group'
    _description = "Technical model to group PO for call to tenders"

    order_ids = fields.One2many('purchase.requisition', 'purchase_requisition_group_id')

    def write(self, vals):
        res = super().write(vals)
        # when len(POs) == 1, only linking PO to itself at this point => self implode (delete) group
        self.filtered(lambda g: len(g.order_ids) <= 1).unlink()
        return res


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    purchase_requisition_group_id = fields.Many2one('purchase.requisition.group')
    alternative_pr_ids2 = fields.One2many(
        'purchase.requisition', related='purchase_requisition_group_id.order_ids',
        string="Alternative PR", check_company=True,
        help="Other potential purchase agreement for requestion products")





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

    def action_link_alternative(self):
        ctx = dict(**self.env.context, default_origin_po_id=self.id)
        return {
            'name': _('Link Agreement Alternative'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.agreement.link.alternative',
            'view_id': self.env.ref('purchase_agreement_alternative.purchase_agreement_link_alternative_form').id,
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
            'domain': [('requisition_id', 'in', (self | self.alternative_pr_ids2).ids)],
            'context': ctx,
        }



class PurchaseRequisitionline(models.Model):
    _inherit = "purchase.requisition.line"

    currency_id = fields.Many2one(string='res.currency', related="requisition_id.currency_id")
    state = fields.Selection('State', related="requisition_id.state")
    vendor_id = fields.Many2one('res.partner', related="requisition_id.vendor_id")


    def action_clear_quantities(self):
        zeroed_lines = self.filtered(lambda l: l.state not in ['cancel', 'open', 'done'])
        zeroed_lines.write({'product_qty': 0})
        if len(self) > len(zeroed_lines):
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Some not cleared"),
                    'message': _("Some quantities were not cleared because their status is not a RFQ status."),
                    'sticky': False,
                }
            }
        return False
    def action_choose(self):
        order_lines = (self.requisition_id | self.requisition_id.alternative_pr_ids).mapped('line_ids')
        order_lines = order_lines.filtered(lambda l: l.product_qty and l.product_id.id in self.product_id.ids and l.id not in self.ids)
        if order_lines:
            return order_lines.action_clear_quantities()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Nothing to clear"),
                'message': _("There are no quantities to clear."),
                'sticky': False,
            }
        }