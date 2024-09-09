from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

from odoo.addons.test_convert.tests.test_env import record

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class mrp_production(models.Model):
    _inherit = "mrp.production"

    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=[],
        compute='_compute_product_id', store=True, copy=True, precompute=True,
        readonly=False, required=True, check_company=True)

    is_costsheet = fields.Boolean('Costsheet')
    sale_costsheet_id = fields.Many2one('sale.order')
    sale_line_costsheet_id = fields.Many2one('sale.order.line')
    suborder_count = fields.Integer(compute="calc_suborder_count")
    requisition_count = fields.Integer(compute="calc_suborder_count")
    timesheet_count = fields.Float(compute="calc_suborder_count")
    mrp_production_id = fields.Many2one('mrp.production')
    purchase_requisition_id = fields.Many2one('purchase.requisition', )
    @api.onchange('is_costsheet')
    def check_onchange_is_costsheet(self):
        for record in self:
            if not record.is_costsheet:
                return {'domain':{'product_id':[('type', 'in', ['product', 'consu'])]}}

    def action_view_suborder(self):
        return {
            'name': _('Costsheet Sub Orders'),
            'view_mode': 'tree,form',
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('mrp_production_id', '=', self.id)],
            'context':{'default_mrp_production_id': self.id}
        }

    def action_view_requisition(self):
        requisition_objs = self.env['purchase.requisition'].sudo().search([('mrp_production_id', '=', self.id)])
        requisition = requisition_objs.ids
        if requisition_objs and self.purchase_requisition_id and self.purchase_requisition_id.id not in requisition_objs.ids:
            # requisition_objs.ids.append(self.purchase_requisition_id.id)
            requisition.append(self.purchase_requisition_id.id)
        return {
            'name': _('Purchase Requisition'),
            'view_mode': 'tree,form',
            'res_model': 'purchase.requisition',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('id', 'in', requisition)],
            # 'context': {'default_mrp_production_id': self.id}
        }
    def action_view_timesheet(self):
        account_analytic_line_employee_list = []
        for record in self:
            for components_obj  in record.move_raw_ids:
                if components_obj.product_id and components_obj.product_id.is_fleet and components_obj.product_id.fleet_vehicle_id and components_obj.product_id.fleet_vehicle_id.is_employee and components_obj.product_id.fleet_vehicle_id.hr_employee_id:
                    account_analytic_line_employee_list.append(components_obj.product_id.fleet_vehicle_id.hr_employee_id.id)
                if components_obj.product_id and components_obj.product_id.is_equipment and components_obj.product_id.maintenance_equipment_id and components_obj.product_id.maintenance_equipment_id.is_employee and components_obj.product_id.maintenance_equipment_id.hr_employee_id:
                    account_analytic_line_employee_list.append(components_obj.product_id.maintenance_equipment_id.hr_employee_id.id)
        timesheet_objs = self.env['account.analytic.line'].sudo().search([('employee_id','in',account_analytic_line_employee_list), ('validated_status','=','validated')])
        account_analytic_line_list=[]
        if timesheet_objs:
            account_analytic_line_list = timesheet_objs.ids
        return {
            'name': _('Timesheet'),
            'view_mode': 'tree,form',
            'res_model': 'account.analytic.line',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('id', 'in', account_analytic_line_list)],
            # 'context': {'default_mrp_production_id': self.id}
        }


    def calc_suborder_count(self):
        for record in self:
            account_analytic_line_employee_list = []
            record.suborder_count = self.search_count([('mrp_production_id','=',record.id)])
            record.requisition_count = self.env['purchase.requisition'].sudo().search_count([('mrp_production_id', '=', record.id)])
            requisition_objs = self.env['purchase.requisition'].sudo().search([('mrp_production_id', '=', record.id)])
            if requisition_objs and self.purchase_requisition_id and self.purchase_requisition_id.id not in requisition_objs.ids:
                record.requisition_count = len(requisition_objs) + 1
            for components_obj  in record.move_raw_ids:
                if components_obj.product_id and components_obj.product_id.is_fleet and components_obj.product_id.fleet_vehicle_id and components_obj.product_id.fleet_vehicle_id.is_employee and components_obj.product_id.fleet_vehicle_id.hr_employee_id:
                    account_analytic_line_employee_list.append(components_obj.product_id.fleet_vehicle_id.hr_employee_id.id)
                if components_obj.product_id and components_obj.product_id.is_equipment and components_obj.product_id.maintenance_equipment_id and components_obj.product_id.maintenance_equipment_id.is_employee and components_obj.product_id.maintenance_equipment_id.hr_employee_id:
                    account_analytic_line_employee_list.append(components_obj.product_id.maintenance_equipment_id.hr_employee_id.id)
            timesheet_objs = self.env['account.analytic.line'].sudo().search(
                [('employee_id', 'in', account_analytic_line_employee_list), ('validated_status', '=', 'validated')])
            record.timesheet_count = sum(timesheet_obj.unit_amount for timesheet_obj in timesheet_objs)

    def action_create_suborder(self):
        self.ensure_one()
        wizard_mrp_suborders = []
        for move_raw_obj in self.move_raw_ids:
            wizard_mrp_suborder_id = self.env['mrp.suborders.details'].sudo().create({
                'mrp_manufacture_line_id': move_raw_obj.id,
                'product_id': move_raw_obj.product_id.id,
                'product_uom_qty': move_raw_obj.product_uom_qty,
                'delivery_qty': move_raw_obj.qty_orders,
                'remaining_qty': move_raw_obj.remaining_qty,
                'upconsume_qty': move_raw_obj.upconsume_qty,
                'quantity': 0.0,

            })
            wizard_mrp_suborders.append(wizard_mrp_suborder_id.id)
        if wizard_mrp_suborders:
            new_wizard = self.env['mrp.suborders'].sudo().create({
                'mrp_manufacture_id': self.id,
                'mrp_suborders_details_ids': [(6, 0, wizard_mrp_suborders)],
            })
            return {
                'name': _('Costsheet Sub Orders'),
                'view_mode': 'form',
                'res_model': 'mrp.suborders',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': new_wizard.id,
            }

    def action_create_agreement(self):
        new_wizard = self.env['manufacture.agreement'].sudo().create({})
        if len(self)>1:
            return {
                'name': _('Agreement Order'),
                'view_mode': 'form',
                'res_model': 'manufacture.agreement',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'context': {},
                'target': 'new',
                'res_id': new_wizard.id,
            }
        else:
            new_wizard = self.env['manufacture.agreement'].sudo().create({
                'mrp_production_id': self.id,
            })
            return {
                'name': _('Agreement Order'),
                'view_mode': 'form',
                'res_model': 'manufacture.agreement',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'context': {'default_mrp_production_id': self.id, 'default_product_id': self.product_id.id},
                'target': 'new',
                'res_id': new_wizard.id,
            }

    def action_add_from_catalog(self):
        order = self.browse(self.env.context.get('order_id'))
        return order.action_add_from_catalog()

    def _get_moves_raw_values(self):
        moves = []
        for production in self:
            if not production.bom_id:
                continue
            factor = production.product_uom_id._compute_quantity(production.product_qty,
                                                                 production.bom_id.product_uom_id) / production.bom_id.product_qty
            boms, lines = production.bom_id.explode(production.product_id, factor,
                                                    picking_type=production.bom_id.picking_type_id)
            for bom_line, line_data in lines:
                if bom_line.child_bom_id and bom_line.child_bom_id.type == 'phantom' :
                    continue
                operation = bom_line.operation_id.id or line_data['parent_line'] and line_data[
                    'parent_line'].operation_id.id
                moves.append(production._get_move_raw_values(
                    bom_line.product_id,
                    line_data['qty'],
                    bom_line.product_uom_id,
                    operation,
                    bom_line
                ))
        return moves

class stock_move(models.Model):
    _inherit = "stock.move"

    origin_qty = fields.Float('Origin Quantity')
    planned_price = fields.Float('Planned Price')

    # quantity = fields.Float(compute="calc_qty_orders", string='Quantity', readonly=False, help="Quantity SubOrder", )
    qty_orders = fields.Float(compute="calc_qty_orders", string='D S', help="Delivery SubOrder", )
    remaining_qty = fields.Float(compute="calc_qty_orders", string='R S ', help="Remaining SubOrder", )
    upconsume_qty = fields.Float(compute="calc_qty_orders", string='Up C S ', help="Up Consume SubOrder", )
    qty_orders_cost = fields.Float(compute="calc_qty_orders", string='D S Cost', help="Delivery SubOrder", )
    remaining_qty_cost = fields.Float(compute="calc_qty_orders", string='R S Cost', help="Remaining SubOrder", )
    upconsume_qty_cost = fields.Float(compute="calc_qty_orders", string='Up C S Cost', help="Up Consume SubOrder", )

    qty_agreement = fields.Float(compute="calc_qty_orders", string='Q A', help="Delivery Agreement", )
    qty_orders_agreement = fields.Float(compute="calc_qty_orders", string='D A', help="Delivery Agreement", )
    remaining_qty_agreement = fields.Float(compute="calc_qty_orders", string='R A ', help="Remaining Agreement", )
    upconsume_qty_agreement = fields.Float(compute="calc_qty_orders", string='Up C A', help="Up Consume Agreement", )

    qty_orders_agreement_cost = fields.Float(compute="calc_qty_orders", string='D A Cost', help="Delivery Agreement", )
    remaining_qty_agreement_cost = fields.Float(compute="calc_qty_orders", string='R A Cost', help="Remaining Agreement", )
    upconsume_qty_agreement_cost = fields.Float(compute="calc_qty_orders", string='Up C A Cost', help="Up Consume Agreement", )

    constru_standard_price = fields.Float('Cost Price', related="product_id.standard_price", store=True)
    constru_unit_price = fields.Float(compute="calc_constru_unit_price", string='Unit Price' )
    @api.model
    def create(self, vals):
        if 'product_uom_qty' in vals and vals.get('product_uom_qty') > 0.0:
            vals['origin_qty'] = vals.get('product_uom_qty')
        return super(stock_move, self).create(vals)

    @api.depends('raw_material_production_id', 'product_id')
    def calc_constru_unit_price(self):
        for record in self:
            record.constru_unit_price = 0.0
            purchase_requisition_line_obj = self.env['purchase.requisition.line'].sudo().search(
                [
                    ('product_id','=',record.product_id.id),
                    ('requisition_id.mrp_production_id','=',record.raw_material_production_id.id),
                    ('requisition_id.state', 'not in', ['draft','cancel']),
                ], limit=1
            )
            if purchase_requisition_line_obj :
                record.constru_unit_price = purchase_requisition_line_obj.price_unit
    def calc_qty_orders(self):
        for record in self:
            qty_orders = 0.0
            record.qty_orders = qty_orders
            record.upconsume_qty = 0.0
            record.remaining_qty = 0.0
            record.upconsume_qty_agreement = 0.0
            record.remaining_qty_agreement = 0.0
            qty_orders_agreement = 0.0
            qty_agreement = 0.0
            mrp_suborders_objs = self.env['mrp.production'].sudo().search([('mrp_production_id','=',record.raw_material_production_id.id)])
            for mrp_suborders_obj in mrp_suborders_objs:
                for move_raw_obj in mrp_suborders_obj.move_raw_ids:
                    if move_raw_obj.product_id == record.product_id:
                        qty_orders += move_raw_obj.product_qty
            record.qty_orders = qty_orders
            if qty_orders > record.product_uom_qty:
                record.upconsume_qty = qty_orders - record.product_uom_qty
            else:
                record.remaining_qty = record.origin_qty - qty_orders
            # record.quantity = qty_orders
            # if not record.raw_material_production_id.mrp_production_id:
            #     record.product_uom_qty = record.product_uom_qty - record.qty_orders

            record.qty_orders_cost = qty_orders * record.constru_standard_price
            record.remaining_qty_cost = record.remaining_qty * record.constru_standard_price
            record.upconsume_qty_cost = record.upconsume_qty * record.constru_standard_price


            purchase_requisition_objs = self.env['purchase.requisition'].sudo().search([('mrp_production_id', '=', record.raw_material_production_id.id)])
            for purchase_requisition_obj in purchase_requisition_objs:
                for move_raw_obj in purchase_requisition_obj.line_ids:
                    if move_raw_obj.product_id == record.product_id:
                        qty_orders_agreement += move_raw_obj.qty_ordered
                        qty_agreement += move_raw_obj.product_qty
            record.qty_orders_agreement = qty_orders_agreement
            record.qty_agreement = qty_agreement


            if qty_orders_agreement > qty_agreement:
                record.upconsume_qty_agreement = qty_orders_agreement - qty_agreement
            else:
                record.remaining_qty_agreement = qty_agreement - qty_orders_agreement

            record.qty_orders_agreement_cost = record.qty_orders_agreement * record.constru_unit_price
            record.remaining_qty_agreement_cost = record.remaining_qty_agreement * record.constru_unit_price
            record.upconsume_qty_agreement_cost = record.upconsume_qty_agreement * record.constru_unit_price