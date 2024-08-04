from odoo import api, fields, models

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    approval_type = fields.Selection(related="category_id.approval_type")
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type')
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", copy=False,)

    def action_confirm(self):
        for request in self:
            if request.category_id.approval_type == 'create_transfer':
                vals = []
                for rec in self.product_line_ids:
                    dic_data = {
                        'product_id': rec.product_id.id,
                        'name': rec.description,
                        'product_uom_qty': rec.quantity,
                        'location_id': rec.approval_request_id.picking_type_id.default_location_src_id.id,
                        'location_dest_id': rec.approval_request_id.picking_type_id.default_location_dest_id.id,
                        # 'price_unit': rec.price_unit,
                    }
                    vals.append((0, 0, dic_data))
                picking = self.env['stock.picking'].create({
                    'partner_id': self.request_owner_id.id,
                    'picking_type_id': self.picking_type_id.id,
                    'analytic_account_id': self.analytic_account_id.id,
                    'location_id': self.picking_type_id.default_location_src_id.id,
                    'location_dest_id': self.picking_type_id.default_location_dest_id.id,
                    'move_ids': vals,
                })

        return super().action_confirm()
