from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging
from datetime import datetime, timedelta
_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class sale_order(models.Model):
    _inherit = "sale.order"

    is_costsheet = fields.Boolean('Costsheet')
    costsheet_count = fields.Integer( compute="calc_costsheet_count")
    requisition_count= fields.Integer( compute="calc_costsheet_count")
    suborder_count = fields.Integer(compute="calc_costsheet_count")
    is_retention_ar = fields.Boolean('Is Retention')
    rentention_dis_type = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')], 'Type')
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

    project_startdate = fields.Date('Project Start Date', trace=True)
    project_enddate = fields.Date('Project Start Date', trace=True)
    is_warehouse = fields.Boolean('IS Warehouse')
    project_task_type_ids = fields.Many2many('project.task.type', string="Project Stages")
    can_see_contract_terms = fields.Boolean('Can See Contract Terms', compute="calc_can_see_contract_terms")

    product_amount_is_discount = fields.Float(string= 'Is Discount Amount', compute="calc_product_type_amount")
    product_amount_refundable = fields.Float(string= 'Is Refundable Amount', compute="calc_product_type_amount")
    product_amount_subcontractor = fields.Float(string= 'Is Subcontractor Amount', compute="calc_product_type_amount")
    product_amount_additional = fields.Float(string= 'Is Additional Amount', compute="calc_product_type_amount")
    product_amount_variation_Order = fields.Float(string= 'Is Variation Order Amount', compute="calc_product_type_amount")
    product_amount_wages = fields.Float(string= 'Is Wages Amount', compute="calc_product_type_amount")
    product_amount_supplier = fields.Float(string= 'Is Supplier Amount', compute="calc_product_type_amount")
    product_amount_customer = fields.Float(string= 'Is Customer Amount', compute="calc_product_type_amount")
    product_amount_costsheet = fields.Float(string= 'Is Costsheet Amount', compute="calc_product_type_amount")

    @api.depends('order_line')
    def calc_product_type_amount(self):
        for record in self:
            product_amount_dict={
                'product_amount_is_discount':0.0,
                'product_amount_refundable': 0.0,
                'product_amount_subcontractor': 0.0,
                'product_amount_additional': 0.0,
                'product_amount_variation_Order': 0.0,
                'product_amount_wages': 0.0,
                'product_amount_supplier': 0.0,
                'product_amount_customer': 0.0,
                'product_amount_costsheet': 0.0,
            }
            for sale_line_obj in record.order_line:
                if sale_line_obj.product_id and sale_line_obj.product_id.is_discount:
                    product_amount_dict['product_amount_is_discount'] += sale_line_obj.price_total
                elif sale_line_obj.product_id and sale_line_obj.product_id.refundable:
                    product_amount_dict['product_amount_refundable'] += sale_line_obj.price_total
                elif sale_line_obj.product_id and sale_line_obj.product_id.subcontractor:
                    product_amount_dict['product_amount_subcontractor'] += sale_line_obj.price_total
                elif sale_line_obj.product_id and sale_line_obj.product_id.additional:
                    product_amount_dict['product_amount_additional'] += sale_line_obj.price_total
                elif sale_line_obj.product_id and sale_line_obj.product_id.variation_Order:
                    product_amount_dict['product_amount_variation_Order'] += sale_line_obj.price_total
                elif sale_line_obj.product_id and sale_line_obj.product_id.wages:
                    product_amount_dict['product_amount_wages'] += sale_line_obj.price_total
                elif sale_line_obj.product_id and sale_line_obj.product_id.supplier:
                    product_amount_dict['product_amount_supplier'] += sale_line_obj.price_total
                elif sale_line_obj.product_id and sale_line_obj.product_id.customer:
                    product_amount_dict['product_amount_customer'] += sale_line_obj.price_total
                elif sale_line_obj.product_id and sale_line_obj.product_id.costsheet:
                    product_amount_dict['product_amount_costsheet'] += sale_line_obj.price_total
            record.product_amount_is_discount = product_amount_dict['product_amount_is_discount']
            record.product_amount_refundable = product_amount_dict['product_amount_refundable']
            record.product_amount_subcontractor = product_amount_dict['product_amount_subcontractor']
            record.product_amount_additional = product_amount_dict['product_amount_additional']
            record.product_amount_variation_Order = product_amount_dict['product_amount_variation_Order']
            record.product_amount_wages = product_amount_dict['product_amount_wages']
            record.product_amount_supplier = product_amount_dict['product_amount_supplier']
            record.product_amount_customer = product_amount_dict['product_amount_customer']
            record.product_amount_costsheet = product_amount_dict['product_amount_costsheet']

    def calc_can_see_contract_terms(self):
        for record in self:
            record.can_see_contract_terms = False
            if self.user_has_groups('sale_costsheet.group_costsheet_contract_terms'):
                record.can_see_contract_terms=True

    def calc_costsheet_total_amount(self):
        for record in self:
            retention_ar_amount = 0.0
            advanced_ar_amount = 0.0
            insurance_ar_amount = 0.0
            costsheet_inv_total_amount = 0.0
            retention_ar_default_product_id = self.env.user.company_id.retention_ar_default_product_id
            advanced_ar_default_product_id = self.env.user.company_id.advanced_ar_default_product_id
            insurance_ar_default_product_id = self.env.user.company_id.insurance_ar_default_product_id
            account_move_objs = self.env['account.move'].sudo().search(
                [('state', 'in', ['draft', 'posted']), '|', ('cons_sale_id', '=', record.id),
                 ('invoice_origin', '=', record.name)])
            for account_move_obj in account_move_objs:
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

    def create_sale_costsheet(self):
        for record in self:
            for sale_line_obj in record.order_line:
                if sale_line_obj.mrp_production_costsheet_id:
                    sale_line_obj.mrp_production_costsheet_id.write({'product_id': sale_line_obj.product_id.id,
                                                                     'product_qty': sale_line_obj.product_uom_qty})
                else:
                    if sale_line_obj.product_id.costsheet:
                        mrp_dic = {
                            'origin': self.name,
                            'product_id': sale_line_obj.product_id.id,
                            'product_qty': sale_line_obj.product_uom_qty,
                            'sale_costsheet_id': record.id,
                            'sale_line_costsheet_id': sale_line_obj.id,
                            'is_costsheet': True
                        }
                        if self.env['stock.picking.type'].sudo().search(
                                [('code', '=', 'mrp_operation'), ('warehouse_id', '=', record.warehouse_id.id)],
                                limit=1):
                            mrp_dic.update({
                                'picking_type_id': self.env['stock.picking.type'].sudo().search(
                                    [('code', '=', 'mrp_operation'), ('warehouse_id', '=', record.warehouse_id.id)],
                                    limit=1).id
                            })
                        mrp_production_costsheet_obj = sale_line_obj.mrp_production_costsheet_id.create(mrp_dic)
                        sale_line_obj.mrp_production_costsheet_id = mrp_production_costsheet_obj.id
                        sale_line_obj.mrp_production_costsheet_id.message_post_with_source(
                            'mail.message_origin_link',
                            render_values={'self': sale_line_obj.mrp_production_costsheet_id, 'origin': self,
                                           'edit': True},
                            subtype_xmlid='mail.mt_note',
                        )
        return True

    def action_view_costsheet(self):
        action = self.env['ir.actions.actions']._for_xml_id('sale_costsheet.mrp_production_costsheet_action')
        mrp_costsheet_ids = self.order_line.mapped('mrp_production_costsheet_id').ids
        action['domain'] = [('id', 'in', mrp_costsheet_ids)]
        return action
    def action_view_suborder(self):
        action = self.env['ir.actions.actions']._for_xml_id('sale_costsheet.mrp_production_costsheet_action')
        mrp_costsheet_ids = self.order_line.mapped('mrp_production_costsheet_id').ids
        action['domain'] = [('mrp_production_id', 'in', mrp_costsheet_ids)]
        return action


    def action_view_requisition(self):
        action = self.env['ir.actions.actions']._for_xml_id('purchase_requisition.action_purchase_requisition')
        mrp_costsheet_ids = self.order_line.mapped('mrp_production_costsheet_id')
        purchase_requisition_obj = self.env['purchase.requisition'].sudo().search([('mrp_production_id', 'in', mrp_costsheet_ids.ids)])
        action['domain'] = [('id', 'in', purchase_requisition_obj.ids)]
        return action

    def calc_costsheet_count(self):
        self.costsheet_count = len(self.order_line.mapped('mrp_production_costsheet_id'))
        costsheet_obj = self.order_line.mapped('mrp_production_costsheet_id')
        self.requisition_count = self.env['purchase.requisition'].sudo().search_count([('mrp_production_id', 'in', costsheet_obj.ids)])
        self.suborder_count = self.env['mrp.production'].sudo().search_count([('mrp_production_id', '=', costsheet_obj.ids)])



    def _prepare_invoice(self):
        invoice_vals = super(sale_order, self)._prepare_invoice()
        invoice_vals['cons_sale_id'] = self.id
        return invoice_vals

    def action_confirm(self):
        for order in self:
            if order.is_warehouse and not self.env['stock.warehouse'].sudo().search([('code','=',f'{order.name.upper()}')]):
                warehouse = self.env['stock.warehouse'].sudo().create({
                    'name': f'{order.name} Warehouse',
                    'code': f'{order.name.upper()}',
                })
                order.warehouse_id = warehouse.id
        return super(sale_order, self).action_confirm()



class sale_order_line(models.Model):
    _inherit = "sale.order.line"

    mrp_production_costsheet_id = fields.Many2one('mrp.production')

    def _timesheet_create_project(self):
        project = super(sale_order_line, self)._timesheet_create_project()
        if self.order_id.project_task_type_ids:
            for project_task_type_obj in self.order_id.project_task_type_ids:
                project_task_type_obj.project_ids = [(4, project.id)]
        return project

    def _timesheet_create_project_prepare_values(self):
        """Generate project values"""
        values = super(sale_order_line, self)._timesheet_create_project_prepare_values()
        if self.order_id and self.order_id.project_startdate and self.order_id.project_enddate:
            values['date_start'] = self.order_id.project_startdate
            values['date'] = self.order_id.project_enddate
        return values

    def _timesheet_create_task_prepare_values(self, project):
        res = super(sale_order_line, self)._timesheet_create_task_prepare_values(project)
        if self.order_id and self.order_id.project_startdate and self.product_id.project_age:
            res.update({'planned_date_begin': self.order_id.project_startdate ,'date_deadline': self.order_id.project_startdate + timedelta(days=self.product_id.project_age)})
        return res