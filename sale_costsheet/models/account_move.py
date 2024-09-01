from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class account_move(models.Model):
    _inherit = "account.move"
    cons_sale_id = fields.Many2one('sale.order')
    costsheet_inv_total_amount = fields.Float('Total Amount', compute="calc_costsheet_total_amount")
    retention_ar_amount = fields.Float('Retention(AR) Amount', compute="calc_costsheet_total_amount")
    advanced_ar_amount = fields.Float('Advanced(AR) Amount', compute="calc_costsheet_total_amount")
    insurance_ar_amount = fields.Float('Insurance(AR) Amount', compute="calc_costsheet_total_amount")

    def calc_costsheet_total_amount(self):
        for record in self:
            retention_ar_amount = 0.0
            advanced_ar_amount = 0.0
            insurance_ar_amount = 0.0
            costsheet_inv_total_amount = 0.0
            retention_ar_default_product_id = self.env.user.company_id.retention_ar_default_product_id
            advanced_ar_default_product_id = self.env.user.company_id.advanced_ar_default_product_id
            insurance_ar_default_product_id = self.env.user.company_id.insurance_ar_default_product_id
            for account_move_obj in self:
                for invoice_line_obj in account_move_obj.invoice_line_ids:
                    if invoice_line_obj.product_id == retention_ar_default_product_id:
                        retention_ar_amount += invoice_line_obj.price_total
                    elif invoice_line_obj.product_id == advanced_ar_default_product_id:
                        advanced_ar_amount += invoice_line_obj.price_total
                    elif invoice_line_obj.product_id == insurance_ar_default_product_id:
                        insurance_ar_amount += invoice_line_obj.price_total
                    else:
                        costsheet_inv_total_amount += invoice_line_obj.price_total
            record.retention_ar_amount = retention_ar_amount
            record.advanced_ar_amount = advanced_ar_amount
            record.insurance_ar_amount = insurance_ar_amount
            record.costsheet_inv_total_amount = costsheet_inv_total_amount


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
                        'price_unit': rentention_amount * -1,
                        'analytic_distribution': {account_move_obj.cons_sale_id.analytic_account_id.id: 100},
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
                        'price_unit': advanced_amount * -1,
                        'analytic_distribution': {account_move_obj.cons_sale_id.analytic_account_id.id: 100},
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
                        'price_unit': insurance_amount * -1,
                        'analytic_distribution': {account_move_obj.cons_sale_id.analytic_account_id.id: 100},
                    }
                )


        return account_move_obj