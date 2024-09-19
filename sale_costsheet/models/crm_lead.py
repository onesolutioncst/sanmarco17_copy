from odoo import api, fields, models, _, Command
class crm_lead(models.Model):
    """ Defines bills of material for a product or a product template """
    _inherit = 'crm.lead'
    purchase_order_id = fields.Many2one('purchase.order', 'Purchase Order')
    account_move_id = fields.Many2one('account.move', 'Vendor Bill')
    rfq_count = fields.Integer('RFQ CO', compute="calc_rfq_count")
    account_move_count = fields.Integer('Bill CO', compute="calc_rfq_count")
    def calc_rfq_count(self):
        for record in self:
            record.rfq_count = self.env['purchase.order'].sudo().search([('crm_lead_id','=',record.id)])
            record.account_move_count = self.env['account.move'].sudo().search([('crm_lead_id', '=', record.id)])

    def open_rfq_crmlead(self):
        rfq_action =  {
            'name': 'New RFQ',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'context': {'default_crm_lead_id': self.id},
            'target': 'new',
        }
        if self.purchase_order_id:
            rfq_action.update({'res_id': self.purchase_order_id.id})
        return rfq_action

    def open_vendor_bill_crmlead(self):
        rfq_action =  {
            'name': 'New Vendor Bill',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'context': {'default_crm_lead_id': self.id,'default_move_type': 'in_invoice', 'display_account_trust': True},
            'target': 'new',
        }
        if self.account_move_id:
            rfq_action.update({'res_id': self.account_move_id.id})
        return rfq_action