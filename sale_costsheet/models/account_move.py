from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class account_move(models.Model):
    _inherit = "account.move"
    cons_sale_id = fields.Many2one('sale.order')

    @api.model
    def create(self, vals):
        account_move_obj = super(account_move, self).create(vals)
        total_amount = account_move_obj.amount_total
        if account_move_obj.cons_sale_id and account_move_obj.cons_sale_id.is_retention_ar and self.env.user.company_id.retention_ar_default_product_id:
            if account_move_obj.cons_sale_id.rentention_dis_type and account_move_obj.cons_sale_id.rentention_dis_type == 'fixed':
                rentention_amount = account_move_obj.cons_sale_id.rentention_amount
            elif account_move_obj.cons_sale_id.rentention_dis_type and account_move_obj.cons_sale_id.rentention_dis_type == 'percentage':
                rentention_amount = account_move_obj.cons_sale_id.rentention_amount * total_amount
            else:
                rentention_amount = 0.0
            if rentention_amount:
                self.env['account.move.line'].sudo().create(
                    {
                        'name': self.env.user.company_id.retention_ar_default_product_id.name,
                        'product_id': self.env.user.company_id.retention_ar_default_product_id.id,
                        'move_id': account_move_obj.id,
                        'quantity': 1,
                        'price_unit': rentention_amount * -1
                        # 'analytic_distribution': False,
                    }
                )
        if account_move_obj.cons_sale_id and account_move_obj.cons_sale_id.is_advanced_ar and self.env.user.company_id.advanced_ar_default_product_id:
            if account_move_obj.cons_sale_id.advanced_dis_type and account_move_obj.cons_sale_id.advanced_dis_type == 'fixed':
                advanced_amount = account_move_obj.cons_sale_id.advanced_amount
            elif account_move_obj.cons_sale_id.advanced_dis_type and account_move_obj.cons_sale_id.advanced_dis_type == 'percentage':
                advanced_amount = account_move_obj.cons_sale_id.advanced_amount * total_amount
            else:
                advanced_amount = 0.0
            if advanced_amount:
                self.env['account.move.line'].sudo().create(
                    {
                        'name': self.env.user.company_id.advanced_ar_default_product_id.name,
                        'product_id': self.env.user.company_id.advanced_ar_default_product_id.id,
                        'move_id': account_move_obj.id,
                        'quantity': 1,
                        'price_unit': advanced_amount * -1
                        # 'analytic_distribution': False,
                    }
                )
        if account_move_obj.cons_sale_id and account_move_obj.cons_sale_id.is_insurance_ar and self.env.user.company_id.insurance_ar_default_product_id:
            if account_move_obj.cons_sale_id.insurance_dis_type and account_move_obj.cons_sale_id.insurance_dis_type == 'fixed':
                insurance_amount = account_move_obj.cons_sale_id.insurance_amount
            elif account_move_obj.cons_sale_id.insurance_dis_type and account_move_obj.cons_sale_id.insurance_dis_type == 'percentage':
                insurance_amount = account_move_obj.cons_sale_id.insurance_amount * total_amount
            else:
                insurance_amount = 0.0
            if insurance_amount:
                self.env['account.move.line'].sudo().create(
                    {
                        'name': self.env.user.company_id.insurance_ar_default_product_id.name,
                        'product_id': self.env.user.company_id.insurance_ar_default_product_id.id,
                        'move_id': account_move_obj.id,
                        'quantity': 1,
                        'price_unit': insurance_amount * -1
                        # 'analytic_distribution': False,
                    }
                )


        return account_move_obj