from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging
from datetime import datetime, timedelta
_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class sale_order(models.Model):
    _inherit = "sale.order"

    is_costsheet = fields.Boolean('Costsheet')
    costsheet_count = fields.Integer('costsheet count', compute="calc_costsheet_count")
    is_retention_ar = fields.Boolean('Is Retention')
    rentention_dis_type = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')], 'Type')
    rentention_amount = fields.Float('Amount')
    is_advanced_ar = fields.Boolean('Is Advanced')
    advanced_dis_type = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')], 'Type')
    advanced_amount = fields.Float('Amount')
    is_insurance_ar = fields.Boolean('Is Insurance')
    insurance_dis_type = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')], 'Type')
    insurance_amount = fields.Float('Amount')

    costsheet_inv_total_amount = fields.Float('Total Amount', compute="calc_costsheet_total_amount")
    retention_ar_amount = fields.Float('Retention(AR) Amount', compute="calc_costsheet_total_amount")
    advanced_ar_amount = fields.Float('Advanced(AR) Amount', compute="calc_costsheet_total_amount")
    insurance_ar_amount = fields.Float('Insurance(AR) Amount', compute="calc_costsheet_total_amount")

    project_startdate = fields.Date('Project Start Date', trace=True)
    project_enddate = fields.Date('Project Start Date', trace=True)
    is_warehouse = fields.Boolean('IS Warehouse')
    project_task_type_ids = fields.Many2many('project.task.type', string="Project Stages")

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
                [('state', '=', ['draft', 'posted']), '|', ('cons_sale_id', '=', record.id),
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

    def calc_costsheet_count(self):
        self.costsheet_count = len(self.order_line.mapped('mrp_production_costsheet_id'))

    def _prepare_invoice(self):
        invoice_vals = super(sale_order, self)._prepare_invoice()
        invoice_vals['cons_sale_id'] = self.id
        return invoice_vals

    def action_confirm(self):
        res = super(sale_order, self).action_confirm()
        for order in self:
            if order.is_warehouse:
                warehouse = self.env['stock.warehouse'].sudo().create({
                    'name': f'{order.name} Warehouse',
                    'code': f'{order.name[:5].upper()}',
                })
                order.warehouse_id = warehouse.id
        return res


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
            res.update({'date_deadline': self.order_id.project_startdate + timedelta(days=self.product_id.project_age)})
        return res