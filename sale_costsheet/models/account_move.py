from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class account_move(models.Model):
    _inherit = "account.move"
    cons_sale_id = fields.Many2one('sale.order')
    cons_purchase_id = fields.Many2one('purchase.order')

    is_retention_ar = fields.Boolean('Is Retention')
    rentention_dis_type = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')], 'Type')
    rentention_amount = fields.Float('Amount')
    is_advanced_ar = fields.Boolean('Is Advanced')
    advanced_dis_type = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')], 'Type')
    advanced_amount = fields.Float('Amount')
    is_insurance_ar = fields.Boolean('Is Insurance')
    insurance_dis_type = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')], 'Type')
    insurance_amount = fields.Float('Amount')

    costsheet_inv_total_amount = fields.Float('Total Amount', compute="calc_costsheet_total_amount", precompute=True, store=True)
    retention_ar_amount = fields.Float('Retention(AR) Amount', compute="calc_costsheet_total_amount", precompute=True, store=True)
    advanced_ar_amount = fields.Float('Advanced(AR) Amount', compute="calc_costsheet_total_amount", precompute=True, store=True)
    insurance_ar_amount = fields.Float('Insurance(AR) Amount', compute="calc_costsheet_total_amount", precompute=True, store=True)

    product_amount_is_discount = fields.Float(string='Is Discount Amount', compute="calc_product_type_amount", precompute=True, store=True)
    product_amount_refundable = fields.Float(string='Is Refundable Amount', compute="calc_product_type_amount", precompute=True, store=True)
    product_amount_subcontractor = fields.Float(string='Is Subcontractor Amount', compute="calc_product_type_amount", precompute=True, store=True)
    product_amount_additional = fields.Float(string='Is Additional Amount', compute="calc_product_type_amount", precompute=True, store=True)
    product_amount_variation_Order = fields.Float(string='Is Variation Order Amount',
                                                  compute="calc_product_type_amount", precompute=True, store=True)
    product_amount_wages = fields.Float(string='Is Wages Amount', compute="calc_product_type_amount", precompute=True, store=True)
    product_amount_supplier = fields.Float(string='Is Supplier Amount', compute="calc_product_type_amount", precompute=True, store=True)
    product_amount_customer = fields.Float(string='Is Customer Amount', compute="calc_product_type_amount", precompute=True, store=True)
    product_amount_costsheet = fields.Float(string='Is Costsheet Amount', compute="calc_product_type_amount", precompute=True, store=True)
    crm_lead_id = fields.Many2one('crm.lead', 'LEAD/Opportunity')

    can_see_contract_terms = fields.Boolean('Can See Contract Terms', compute="calc_can_see_contract_terms")
    def calc_can_see_contract_terms(self):
        for record in self:
            record.can_see_contract_terms = False
            if self.user_has_groups('sale_costsheet.group_costsheet_contract_terms'):
                record.can_see_contract_terms=True



    @api.depends('invoice_line_ids')
    def calc_product_type_amount(self):
        for record in self:
            product_amount_dict = {
                'product_amount_is_discount': 0.0,
                'product_amount_refundable': 0.0,
                'product_amount_subcontractor': 0.0,
                'product_amount_additional': 0.0,
                'product_amount_variation_Order': 0.0,
                'product_amount_wages': 0.0,
                'product_amount_supplier': 0.0,
                'product_amount_customer': 0.0,
                'product_amount_costsheet': 0.0,
            }
            for invoice_line_obj in record.invoice_line_ids:
                if invoice_line_obj.product_id and invoice_line_obj.product_id.is_discount:
                    product_amount_dict['product_amount_is_discount'] += invoice_line_obj.price_total
                elif invoice_line_obj.product_id and invoice_line_obj.product_id.refundable:
                    product_amount_dict['product_amount_refundable'] += invoice_line_obj.price_total
                elif invoice_line_obj.product_id and invoice_line_obj.product_id.subcontractor:
                    product_amount_dict['product_amount_subcontractor'] += invoice_line_obj.price_total
                elif invoice_line_obj.product_id and invoice_line_obj.product_id.additional:
                    product_amount_dict['product_amount_additional'] += invoice_line_obj.price_total
                elif invoice_line_obj.product_id and invoice_line_obj.product_id.variation_Order:
                    product_amount_dict['product_amount_variation_Order'] += invoice_line_obj.price_total
                elif invoice_line_obj.product_id and invoice_line_obj.product_id.wages:
                    product_amount_dict['product_amount_wages'] += invoice_line_obj.price_total
                elif invoice_line_obj.product_id and invoice_line_obj.product_id.supplier:
                    product_amount_dict['product_amount_supplier'] += invoice_line_obj.price_total
                elif invoice_line_obj.product_id and invoice_line_obj.product_id.customer:
                    product_amount_dict['product_amount_customer'] += invoice_line_obj.price_total
                elif invoice_line_obj.product_id and invoice_line_obj.product_id.costsheet:
                    product_amount_dict['product_amount_costsheet'] += invoice_line_obj.price_total
            record.product_amount_is_discount = product_amount_dict['product_amount_is_discount']
            record.product_amount_refundable = product_amount_dict['product_amount_refundable']
            record.product_amount_subcontractor = product_amount_dict['product_amount_subcontractor']
            record.product_amount_additional = product_amount_dict['product_amount_additional']
            record.product_amount_variation_Order = product_amount_dict['product_amount_variation_Order']
            record.product_amount_wages = product_amount_dict['product_amount_wages']
            record.product_amount_supplier = product_amount_dict['product_amount_supplier']
            record.product_amount_customer = product_amount_dict['product_amount_customer']
            record.product_amount_costsheet = product_amount_dict['product_amount_costsheet']


    @api.depends('line_ids')
    def calc_costsheet_total_amount(self):
        for record in self:
            retention_ar_amount = 0.0
            advanced_ar_amount = 0.0
            insurance_ar_amount = 0.0
            costsheet_inv_total_amount = 0.0
            purchase_source_orders = record.line_ids.purchase_line_id.order_id
            sale_source_orders = self.line_ids.sale_line_ids.order_id
            if purchase_source_orders:
                retention_ar_default_product_id = self.env.user.company_id.retention_ap_default_product_id
                advanced_ar_default_product_id = self.env.user.company_id.advanced_ap_default_product_id
                insurance_ar_default_product_id = self.env.user.company_id.insurance_ap_default_product_id
            elif sale_source_orders:
                retention_ar_default_product_id = self.env.user.company_id.retention_ar_default_product_id
                advanced_ar_default_product_id = self.env.user.company_id.advanced_ar_default_product_id
                insurance_ar_default_product_id = self.env.user.company_id.insurance_ar_default_product_id
            else:
                retention_ar_default_product_id = ""
                advanced_ar_default_product_id = ""
                insurance_ar_default_product_id = ""
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
        if account_move_obj.cons_sale_id:
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
        # elif account_move_obj.cons_purchase_id:
        #     if account_move_obj.cons_purchase_id and account_move_obj.cons_purchase_id.is_retention_ar and self.env.user.company_id.retention_ap_default_product_id:
        #         if account_move_obj.cons_purchase_id.rentention_dis_type and account_move_obj.cons_purchase_id.rentention_dis_type == 'fixed':
        #             rentention_amount = account_move_obj.cons_purchase_id.rentention_amount
        #         elif account_move_obj.cons_purchase_id.rentention_dis_type and account_move_obj.cons_purchase_id.rentention_dis_type == 'percentage':
        #             rentention_amount = account_move_obj.cons_purchase_id.rentention_amount * total_amount
        #         else:
        #             rentention_amount = 0.0
        #         if rentention_amount:
        #             self.env['account.move.line'].sudo().create(
        #                 {
        #                     'name': self.env.user.company_id.retention_ap_default_product_id.name,
        #                     'product_id': self.env.user.company_id.retention_ap_default_product_id.id,
        #                     'move_id': account_move_obj.id,
        #                     'quantity': 1,
        #                     'price_unit': rentention_amount * -1,
        #                     # 'analytic_distribution': {account_move_obj.cons_purchase_id.analytic_account_id.id: 100},
        #                 }
        #             )
        #     if account_move_obj.cons_purchase_id and account_move_obj.cons_purchase_id.is_advanced_ar and self.env.user.company_id.advanced_ap_default_product_id:
        #         if account_move_obj.cons_purchase_id.advanced_dis_type and account_move_obj.cons_purchase_id.advanced_dis_type == 'fixed':
        #             advanced_amount = account_move_obj.cons_purchase_id.advanced_amount
        #         elif account_move_obj.cons_purchase_id.advanced_dis_type and account_move_obj.cons_purchase_id.advanced_dis_type == 'percentage':
        #             advanced_amount = account_move_obj.cons_purchase_id.advanced_amount * total_amount
        #         else:
        #             advanced_amount = 0.0
        #         if advanced_amount:
        #             self.env['account.move.line'].sudo().create(
        #                 {
        #                     'name': self.env.user.company_id.advanced_ap_default_product_id.name,
        #                     'product_id': self.env.user.company_id.advanced_ap_default_product_id.id,
        #                     'move_id': account_move_obj.id,
        #                     'quantity': 1,
        #                     'price_unit': advanced_amount * -1,
        #                     # 'analytic_distribution': {account_move_obj.cons_purchase_id.analytic_account_id.id: 100},
        #                 }
        #             )
        #     if account_move_obj.cons_purchase_id and account_move_obj.cons_purchase_id.is_insurance_ar and self.env.user.company_id.insurance_ap_default_product_id:
        #         if account_move_obj.cons_purchase_id.insurance_dis_type and account_move_obj.cons_purchase_id.insurance_dis_type == 'fixed':
        #             insurance_amount = account_move_obj.cons_purchase_id.insurance_amount
        #         elif account_move_obj.cons_purchase_id.insurance_dis_type and account_move_obj.cons_purchase_id.insurance_dis_type == 'percentage':
        #             insurance_amount = account_move_obj.cons_purchase_id.insurance_amount * total_amount
        #         else:
        #             insurance_amount = 0.0
        #         if insurance_amount:
        #             self.env['account.move.line'].sudo().create(
        #                 {
        #                     'name': self.env.user.company_id.insurance_ap_default_product_id.name,
        #                     'product_id': self.env.user.company_id.insurance_ap_default_product_id.id,
        #                     'move_id': account_move_obj.id,
        #                     'quantity': 1,
        #                     'price_unit': insurance_amount * -1,
        #                     # 'analytic_distribution': {account_move_obj.cons_purchase_id.analytic_account_id.id: 100},
        #                 }
        #             )



        if account_move_obj.crm_lead_id:
            account_move_obj.crm_lead_id.account_move_id = account_move_obj.id
        return account_move_obj