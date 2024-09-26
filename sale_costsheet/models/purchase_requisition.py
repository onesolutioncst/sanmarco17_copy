from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging, json

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class purchase_requisition(models.Model):
    _inherit = "purchase.requisition"

    mrp_production_id = fields.Many2one('mrp.production', trace=True)
    milestone_count = fields.Integer(compute='_compute_milestone_count')
    is_retention_ar = fields.Boolean('Is Retention')
    rentention_dis_type = fields.Selection([('fixed','Fixed'), ('percentage','Percentage')], 'Type')
    rentention_amount = fields.Float('Amount')
    is_advanced_ar = fields.Boolean('Is Advanced')
    advanced_dis_type = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')], 'Type')
    advanced_amount = fields.Float('Amount')
    is_insurance_ar = fields.Boolean('Is Insurance')
    insurance_dis_type = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')], 'Type')
    insurance_amount = fields.Float('Amount')

    costsheet_inv_total_amount = fields.Float('Total Amount', compute="calc_costsheet_total_amount", store=True, precompute=True)
    retention_ar_amount = fields.Float('Retention(AR) Amount', compute="calc_costsheet_total_amount", store=True, precompute=True)
    advanced_ar_amount = fields.Float('Advanced(AR) Amount', compute="calc_costsheet_total_amount", store=True, precompute=True)
    insurance_ar_amount = fields.Float('Insurance(AR) Amount', compute="calc_costsheet_total_amount", store=True, precompute=True)

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

    @api.depends('line_ids')
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
            for purchase_requisition_obj in record.line_ids:
                if purchase_requisition_obj.product_id and purchase_requisition_obj.product_id.is_discount:
                    product_amount_dict['product_amount_is_discount'] += purchase_requisition_obj.qty_ordered * purchase_requisition_obj.price_unit
                elif purchase_requisition_obj.product_id and purchase_requisition_obj.product_id.refundable:
                    product_amount_dict['product_amount_refundable'] += purchase_requisition_obj.qty_ordered * purchase_requisition_obj.price_unit
                elif purchase_requisition_obj.product_id and purchase_requisition_obj.product_id.subcontractor:
                    product_amount_dict['product_amount_subcontractor'] += purchase_requisition_obj.qty_ordered * purchase_requisition_obj.price_unit
                elif purchase_requisition_obj.product_id and purchase_requisition_obj.product_id.additional:
                    product_amount_dict['product_amount_additional'] += purchase_requisition_obj.qty_ordered * purchase_requisition_obj.price_unit
                elif purchase_requisition_obj.product_id and purchase_requisition_obj.product_id.variation_Order:
                    product_amount_dict['product_amount_variation_Order'] += purchase_requisition_obj.qty_ordered * purchase_requisition_obj.price_unit
                elif purchase_requisition_obj.product_id and purchase_requisition_obj.product_id.wages:
                    product_amount_dict['product_amount_wages'] += purchase_requisition_obj.qty_ordered * purchase_requisition_obj.price_unit
                elif purchase_requisition_obj.product_id and purchase_requisition_obj.product_id.supplier:
                    product_amount_dict['product_amount_supplier'] += purchase_requisition_obj.qty_ordered * purchase_requisition_obj.price_unit
                elif purchase_requisition_obj.product_id and purchase_requisition_obj.product_id.customer:
                    product_amount_dict['product_amount_customer'] += purchase_requisition_obj.qty_ordered * purchase_requisition_obj.price_unit
                elif purchase_requisition_obj.product_id and purchase_requisition_obj.product_id.costsheet:
                    product_amount_dict['product_amount_costsheet'] += purchase_requisition_obj.qty_ordered * purchase_requisition_obj.price_unit
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
            retention_ar_default_product_id = self.env.user.company_id.retention_ar_default_product_id
            advanced_ar_default_product_id = self.env.user.company_id.advanced_ar_default_product_id
            insurance_ar_default_product_id = self.env.user.company_id.insurance_ar_default_product_id
            purchase_order_objs = self.env['purchase.order'].sudo().search(
                [('state', 'in', ['draft', 'posted']), ('requisition_id', '=', record.id)])
            for purchase_order_obj in purchase_order_objs:
                for order_line_obj in purchase_order_obj.order_line:
                    if order_line_obj.product_id == retention_ar_default_product_id:
                        retention_ar_amount += order_line_obj.price_total
                    elif order_line_obj.product_id == advanced_ar_default_product_id:
                        advanced_ar_amount += order_line_obj.price_total
                    elif order_line_obj.product_id == insurance_ar_default_product_id:
                        insurance_ar_amount += order_line_obj.price_total
                    else:
                        costsheet_inv_total_amount += order_line_obj.price_total
            record.retention_ar_amount = retention_ar_amount
            record.advanced_ar_amount = advanced_ar_amount
            record.insurance_ar_amount = insurance_ar_amount
            record.costsheet_inv_total_amount = costsheet_inv_total_amount

    def action_view_milestone(self):
        return {
            'name': _('Requistion Milestone'),
            'view_mode': 'tree',
            'res_model': 'purchase.requisition.milestone',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('purchase_requisition_id', '=', self.id)],
            'context':{'default_purchase_requisition_id': self.id}
        }

    def action_in_progress(self):
        in_progress = super(purchase_requisition, self).action_in_progress()
        for line_obj in self.line_ids:
            # create milestone
            purchase_requisition_milestone_obj = self.env['purchase.requisition.milestone'].sudo().create(
                {
                    'purchase_requisition_id': self.id,
                    'name': line_obj.product_description_variants,
                    'purchase_requisition_line_id': line_obj.id,
                    'quantity_percentage': 0.0,
                    'product_uom_qty': line_obj.product_qty,
                    'is_reached': True,
                }
            )
            line_obj.purchase_requisition_milestone_id = purchase_requisition_milestone_obj.id
        return in_progress

    def _compute_milestone_count(self):
        for record in self:
            record.milestone_count = self.env['purchase.requisition.milestone'].sudo().search_count([('purchase_requisition_id','=',record.id)])


class purchase_requisition_line(models.Model):
    _inherit = "purchase.requisition.line"

    purchase_requisition_milestone_id = fields.Many2one('purchase.requisition.milestone')
    remaining_qty = fields.Float(compute="calc_qty_orders", string='R A ', help="Remaining QTY")
    upconsume_qty = fields.Float(compute="calc_qty_orders", string='Up C A ', help="Up Consume QTY")
    milestone_qty = fields.Float(string="Milestone QTY", related="purchase_requisition_milestone_id.product_uom_qty")
    remaining_milestone_qty = fields.Float(string="Milestone QTY", compute="calc_remaining_milestone_qty")
    mrp_manufacture_line_id = fields.Many2one('stock.move', 'Components')

    def calc_remaining_milestone_qty(self):
        for record in self:
            purchase_order_line_objs = self.env['purchase.order.line'].sudo().search([('purchase_requisition_line_id','=',record.id)])
            record.remaining_milestone_qty = record.product_qty - sum(purchase_order_line_obj.product_qty for purchase_order_line_obj in purchase_order_line_objs)


    def calc_qty_orders(self):
        for record in self:
            record.remaining_qty = 0.0
            record.upconsume_qty = 0.0
            if record.product_qty > record.qty_ordered:
                record.remaining_qty = record.product_qty - record.qty_ordered
            else:
                record.upconsume_qty = record.qty_ordered - record.product_qty

    def _prepare_purchase_order_line(self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
        res = super(purchase_requisition_line, self)._prepare_purchase_order_line(name, product_qty, price_unit, taxes_ids)
        res['purchase_requisition_line_id'] = self.id
        return res
