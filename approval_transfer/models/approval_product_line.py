from odoo import api, fields, models



class ApprovalProductLine(models.Model):
    _inherit = 'approval.product.line'

    forcasted_available = fields.Float(compute="_compute_on_hand")

    @api.depends('product_id')
    def _compute_on_hand(self):
        for record in self:
            product = record.product_id
            if product:
                record.forcasted_available = product.qty_available + (product.incoming_qty - product.outgoing_qty)
            else:
                record.forcasted_available = 00.00

    def action_product_forecast_report(self):
        self.ensure_one()
        action = self.product_id.action_product_forecast_report()
        action['context'] = {
            'active_id': self.product_id.id,
            'active_model': 'product.product',
            'move_to_match_ids': self.ids
        }
        return action
