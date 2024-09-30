from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class purchase_order(models.Model):
    _inherit = "purchase.order"

    is_retention_ar = fields.Boolean('Is Retention')
    rentention_dis_type = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')], 'Type')
    rentention_amount = fields.Float('Amount')
    is_advanced_ar = fields.Boolean('Is Advanced')
    advanced_dis_type = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')], 'Type')
    advanced_amount = fields.Float('Amount')
    is_insurance_ar = fields.Boolean('Is Insurance')
    insurance_dis_type = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')], 'Type')
    insurance_amount = fields.Float('Amount')
    can_see_contract_terms = fields.Boolean('Can See Contract Terms', compute="calc_can_see_contract_terms")

    costsheet_inv_total_amount = fields.Float('Total Amount', compute="calc_costsheet_total_amount", precompute=True)
    retention_ar_amount = fields.Float('Retention(AR) Amount', compute="calc_costsheet_total_amount", precompute=True)
    advanced_ar_amount = fields.Float('Advanced(AR) Amount', compute="calc_costsheet_total_amount", precompute=True)
    insurance_ar_amount = fields.Float('Insurance(AR) Amount', compute="calc_costsheet_total_amount", precompute=True)




    product_amount_is_discount = fields.Float(string='Is Discount Amount', compute="calc_product_type_amount")
    product_amount_refundable = fields.Float(string='Is Refundable Amount', compute="calc_product_type_amount")
    product_amount_subcontractor = fields.Float(string='Is Subcontractor Amount', compute="calc_product_type_amount")
    product_amount_additional = fields.Float(string='Is Additional Amount', compute="calc_product_type_amount")
    product_amount_variation_Order = fields.Float(string='Is Variation Order Amount',
                                                  compute="calc_product_type_amount")
    product_amount_wages = fields.Float(string='Is Wages Amount', compute="calc_product_type_amount")
    product_amount_supplier = fields.Float(string='Is Supplier Amount', compute="calc_product_type_amount")
    product_amount_customer = fields.Float(string='Is Customer Amount', compute="calc_product_type_amount")
    product_amount_costsheet = fields.Float(string='Is Costsheet Amount', compute="calc_product_type_amount")

    crm_lead_id = fields.Many2one('crm.lead', 'LEAD/Opportunity')

    def calc_can_see_contract_terms(self):
        for record in self:
            record.can_see_contract_terms = False
            if self.user_has_groups('sale_costsheet.group_costsheet_contract_terms'):
                record.can_see_contract_terms=True

    @api.depends('order_line')
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
            for purchase_order_line_obj in record.order_line:
                if purchase_order_line_obj.product_id and purchase_order_line_obj.product_id.is_discount:
                    product_amount_dict['product_amount_is_discount'] += purchase_order_line_obj.price_total
                elif purchase_order_line_obj.product_id and purchase_order_line_obj.product_id.refundable:
                    product_amount_dict['product_amount_refundable'] += purchase_order_line_obj.price_total
                elif purchase_order_line_obj.product_id and purchase_order_line_obj.product_id.subcontractor:
                    product_amount_dict['product_amount_subcontractor'] += purchase_order_line_obj.price_total
                elif purchase_order_line_obj.product_id and purchase_order_line_obj.product_id.additional:
                    product_amount_dict['product_amount_additional'] += purchase_order_line_obj.price_total
                elif purchase_order_line_obj.product_id and purchase_order_line_obj.product_id.variation_Order:
                    product_amount_dict['product_amount_variation_Order'] += purchase_order_line_obj.price_total
                elif purchase_order_line_obj.product_id and purchase_order_line_obj.product_id.wages:
                    product_amount_dict['product_amount_wages'] += purchase_order_line_obj.price_total
                elif purchase_order_line_obj.product_id and purchase_order_line_obj.product_id.supplier:
                    product_amount_dict['product_amount_supplier'] += purchase_order_line_obj.price_total
                elif purchase_order_line_obj.product_id and purchase_order_line_obj.product_id.customer:
                    product_amount_dict['product_amount_customer'] += purchase_order_line_obj.price_total
                elif purchase_order_line_obj.product_id and purchase_order_line_obj.product_id.costsheet:
                    product_amount_dict['product_amount_costsheet'] += purchase_order_line_obj.price_total
            record.product_amount_is_discount = product_amount_dict['product_amount_is_discount']
            record.product_amount_refundable = product_amount_dict['product_amount_refundable']
            record.product_amount_subcontractor = product_amount_dict['product_amount_subcontractor']
            record.product_amount_additional = product_amount_dict['product_amount_additional']
            record.product_amount_variation_Order = product_amount_dict['product_amount_variation_Order']
            record.product_amount_wages = product_amount_dict['product_amount_wages']
            record.product_amount_supplier = product_amount_dict['product_amount_supplier']
            record.product_amount_customer = product_amount_dict['product_amount_customer']
            record.product_amount_costsheet = product_amount_dict['product_amount_costsheet']

    def calc_costsheet_total_amount(self):
        for record in self:
            retention_ar_amount = 0.0
            advanced_ar_amount = 0.0
            insurance_ar_amount = 0.0
            costsheet_inv_total_amount = 0.0
            retention_ar_default_product_id = self.env.user.company_id.retention_ap_default_product_id
            advanced_ar_default_product_id = self.env.user.company_id.advanced_ap_default_product_id
            insurance_ar_default_product_id = self.env.user.company_id.insurance_ap_default_product_id
            for purchase_order_obj in self:
                for purchase_order_line_obj in purchase_order_obj.order_line:
                    if purchase_order_line_obj.product_id == retention_ar_default_product_id:
                        retention_ar_amount += purchase_order_line_obj.price_total
                    elif purchase_order_line_obj.product_id == advanced_ar_default_product_id:
                        advanced_ar_amount += purchase_order_line_obj.price_total
                    elif purchase_order_line_obj.product_id == insurance_ar_default_product_id:
                        insurance_ar_amount += purchase_order_line_obj.price_total
                    else:
                        costsheet_inv_total_amount += purchase_order_line_obj.price_total
            record.retention_ar_amount = retention_ar_amount
            record.advanced_ar_amount = advanced_ar_amount
            record.insurance_ar_amount = insurance_ar_amount
            record.costsheet_inv_total_amount = costsheet_inv_total_amount

    @api.model
    def create(self, vals):
        purchase_obj = super(purchase_order, self).create(vals)
        total_amount = purchase_obj.amount_total
        if purchase_obj.requisition_id and purchase_obj.requisition_id.is_retention_ar and self.env.user.company_id.retention_ap_default_product_id:
            if purchase_obj.requisition_id.rentention_dis_type and purchase_obj.requisition_id.rentention_dis_type == 'fixed':
                rentention_amount = purchase_obj.requisition_id.rentention_amount
            elif purchase_obj.requisition_id.rentention_dis_type and purchase_obj.requisition_id.rentention_dis_type == 'percentage':
                rentention_amount = purchase_obj.requisition_id.rentention_amount * total_amount
            else:
                rentention_amount = 0.0
            if rentention_amount:
                purchase_line_dic = {
                    'name': self.env.user.company_id.retention_ap_default_product_id.name,
                    'product_id': self.env.user.company_id.retention_ap_default_product_id.id,
                    'order_id': purchase_obj.id,
                    'product_qty': 1,
                    'price_unit': rentention_amount * -1
                }
                if purchase_obj.requisition_id and purchase_obj.requisition_id.mrp_production_id and purchase_obj.requisition_id.mrp_production_id.analytic_distribution:
                    purchase_line_dic.update(
                        {'analytic_distribution': purchase_obj.requisition_id.mrp_production_id.analytic_distribution})
                self.env['purchase.order.line'].sudo().create(purchase_line_dic)
            purchase_obj.is_retention_ar = purchase_obj.requisition_id.is_retention_ar
            purchase_obj.rentention_dis_type = purchase_obj.requisition_id.rentention_dis_type
            purchase_obj.rentention_amount = purchase_obj.requisition_id.rentention_amount

        if purchase_obj.requisition_id and purchase_obj.requisition_id.is_advanced_ar and self.env.user.company_id.advanced_ap_default_product_id:
            if purchase_obj.requisition_id.advanced_dis_type and purchase_obj.requisition_id.advanced_dis_type == 'fixed':
                advanced_amount = purchase_obj.requisition_id.advanced_amount
            elif purchase_obj.requisition_id.advanced_dis_type and purchase_obj.requisition_id.advanced_dis_type == 'percentage':
                advanced_amount = purchase_obj.requisition_id.advanced_amount * total_amount
            else:
                advanced_amount = 0.0
            if advanced_amount:
                purchase_line_dic = {
                    'name': self.env.user.company_id.advanced_ap_default_product_id.name,
                    'product_id': self.env.user.company_id.advanced_ap_default_product_id.id,
                    'order_id': purchase_obj.id,
                    'product_qty': 1,
                    'price_unit': advanced_amount * -1
                }
                if purchase_obj.requisition_id and purchase_obj.requisition_id.mrp_production_id and purchase_obj.requisition_id.mrp_production_id.analytic_distribution:
                    purchase_line_dic.update(
                        {'analytic_distribution': purchase_obj.requisition_id.mrp_production_id.analytic_distribution})
                self.env['purchase.order.line'].sudo().create(purchase_line_dic)
            purchase_obj.is_advanced_ar = purchase_obj.requisition_id.is_advanced_ar
            purchase_obj.advanced_dis_type = purchase_obj.requisition_id.advanced_dis_type
            purchase_obj.advanced_amount = purchase_obj.requisition_id.advanced_amount

        if purchase_obj.requisition_id and purchase_obj.requisition_id.is_insurance_ar and self.env.user.company_id.insurance_ap_default_product_id:
            if purchase_obj.requisition_id.insurance_dis_type and purchase_obj.requisition_id.insurance_dis_type == 'fixed':
                insurance_amount = purchase_obj.requisition_id.insurance_amount
            elif purchase_obj.requisition_id.insurance_dis_type and purchase_obj.requisition_id.insurance_dis_type == 'percentage':
                insurance_amount = purchase_obj.requisition_id.insurance_amount * total_amount
            else:
                insurance_amount = 0.0
            if insurance_amount:
                purchase_line_dic = {
                    'name': self.env.user.company_id.insurance_ap_default_product_id.name,
                    'product_id': self.env.user.company_id.insurance_ap_default_product_id.id,
                    'order_id': purchase_obj.id,
                    'product_qty': 1,
                    'price_unit': insurance_amount * -1
                }
                if purchase_obj.requisition_id and purchase_obj.requisition_id.mrp_production_id and purchase_obj.requisition_id.mrp_production_id.analytic_distribution:
                    purchase_line_dic.update(
                        {'analytic_distribution': purchase_obj.requisition_id.mrp_production_id.analytic_distribution})
                self.env['purchase.order.line'].sudo().create(purchase_line_dic)
            purchase_obj.is_insurance_ar = purchase_obj.requisition_id.is_insurance_ar
            purchase_obj.insurance_dis_type = purchase_obj.requisition_id.insurance_dis_type
            purchase_obj.insurance_amount = purchase_obj.requisition_id.insurance_amount

        if purchase_obj.crm_lead_id:
            purchase_obj.crm_lead_id.purchase_order_id = purchase_obj.id



        return purchase_obj

    def check_see_rfq(self, requisition_id):
        for record in requisition_id:
            for line_obj in record.line_ids:
                purchase_order_line_objs = self.env['purchase.order.line'].sudo().search(
                    [('purchase_requisition_line_id', '=', line_obj.id)])
                remaining_milestone_qty = sum(
                    purchase_order_line_obj.product_qty for purchase_order_line_obj in purchase_order_line_objs)
                if line_obj.milestone_qty > remaining_milestone_qty:
                    return True
        return False

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        if not self.requisition_id:
            return

        self = self.with_company(self.company_id)
        if not self.check_see_rfq(self.requisition_id):
            raise ValidationError(_("Sorry No Quantity to Invoice"))

        requisition = self.requisition_id
        if self.partner_id:
            partner = self.partner_id
        else:
            partner = requisition.vendor_id
        payment_term = partner.property_supplier_payment_term_id

        FiscalPosition = self.env['account.fiscal.position']
        fpos = FiscalPosition.with_company(self.company_id)._get_fiscal_position(partner)

        self.partner_id = partner.id
        self.fiscal_position_id = fpos.id
        self.payment_term_id = payment_term.id
        self.company_id = requisition.company_id.id
        self.currency_id = requisition.currency_id.id
        if not self.origin or requisition.name not in self.origin.split(', '):
            if self.origin:
                if requisition.name:
                    self.origin = self.origin + ', ' + requisition.name
            else:
                self.origin = requisition.name
        self.notes = requisition.description
        self.date_order = fields.Datetime.now()

        if requisition.type_id.line_copy != 'copy':
            return

        # Create PO lines if necessary
        order_lines = []
        for line in requisition.line_ids:
            # Compute name
            product_lang = line.product_id.with_context(
                lang=partner.lang or self.env.user.lang,
                partner_id=partner.id
            )
            name = product_lang.display_name
            if product_lang.description_purchase:
                name += '\n' + product_lang.description_purchase

            # Compute taxes
            taxes_ids = fpos.map_tax(
                line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id)).ids

            # Compute quantity and price_unit

            if line.product_uom_id != line.product_id.uom_po_id:
                product_qty = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_po_id)
                price_unit = line.product_uom_id._compute_price(line.price_unit, line.product_id.uom_po_id)
            else:
                product_qty = line.product_qty
                price_unit = line.price_unit

            if requisition.type_id.quantity_copy != 'copy':
                product_qty = 0
            milestone_qty = line.milestone_qty
            purchase_order_line_objs = self.env['purchase.order.line'].sudo().search(
                [('purchase_requisition_line_id', '=', line.id)])
            done_milestone_qty = sum(
                purchase_order_line_obj.product_qty for purchase_order_line_obj in purchase_order_line_objs)
            product_qty = milestone_qty - done_milestone_qty
            # Create PO line
            if product_qty != 0:
                order_line_values = line._prepare_purchase_order_line(
                    name=name, product_qty=product_qty, price_unit=price_unit,
                    taxes_ids=taxes_ids)
                order_lines.append((0, 0, order_line_values))
        self.order_line = order_lines

    def button_confirm(self):
        res = super(purchase_order, self).button_confirm()
        for record in self:
            for purchase_order_line_obj in record.order_line:
                if purchase_order_line_obj.purchase_requisition_line_id and purchase_order_line_obj.purchase_requisition_line_id.mrp_manufacture_line_id:
                    if purchase_order_line_obj.purchase_requisition_line_id.mrp_manufacture_line_id.product_uom_qty > purchase_order_line_obj.product_qty:
                        purchase_order_line_obj.purchase_requisition_line_id.mrp_manufacture_line_id.product_uom_qty = purchase_order_line_obj.purchase_requisition_line_id.mrp_manufacture_line_id.product_uom_qty - purchase_order_line_obj.product_qty
                    else:
                        purchase_order_line_obj.purchase_requisition_line_id.mrp_manufacture_line_id.total_up = purchase_order_line_obj.product_qty - purchase_order_line_obj.purchase_requisition_line_id.mrp_manufacture_line_id.product_uom_qty
        return res

    def _prepare_invoice(self):
        invoice_vals = super(purchase_order, self)._prepare_invoice()
        invoice_vals['cons_purchase_id'] = self.id
        invoice_vals['is_retention_ar'] = self.is_retention_ar
        invoice_vals['rentention_dis_type'] = self.rentention_dis_type
        invoice_vals['rentention_amount'] = self.rentention_amount
        invoice_vals['is_advanced_ar'] = self.is_advanced_ar
        invoice_vals['advanced_dis_type'] = self.advanced_dis_type
        invoice_vals['advanced_amount'] = self.advanced_amount
        invoice_vals['is_insurance_ar'] = self.is_insurance_ar
        invoice_vals['insurance_dis_type'] = self.insurance_dis_type
        invoice_vals['insurance_amount'] = self.insurance_amount
        return invoice_vals

class purchase_order_line(models.Model):
    _inherit = "purchase.order.line"

    purchase_requisition_line_id = fields.Many2one('purchase.requisition.line')
