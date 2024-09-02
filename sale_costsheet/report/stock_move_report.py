# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class stock_move_report(models.Model):
    _name = "stock.move.report"
    _description = "Costsheet Moves Analysis Report"
    _auto = False
    _rec_name = 'name'

    name = fields.Char(string="Costsheet Reference", readonly=True)
    date_start = fields.Datetime(string="Order Date", readonly=True)
    date_finished = fields.Datetime(string="Date Finished", readonly=True)
    main_product_id = fields.Many2one(comodel_name='product.product', string="Product", readonly=True)
    sub_product_id = fields.Many2one(comodel_name='product.product', string="Sub Product", readonly=True)
    product_packaging_id = fields.Many2one('product.packaging', string="Packaging", readonly=True)
    location_id = fields.Many2one('stock.location', string="From", readonly=True)
    product_uom_qty = fields.Float('To Consumne', readonly=True)
    quantity = fields.Float('Quantity', readonly=True)
    product_uom = fields.Many2one('uom.uom', 'UOM', readonly=True)
    picked = fields.Boolean('Picked', readonly=True)
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', readonly=True)
    location_dest_id = fields.Many2one('stock.location', 'Destination Location', readonly=True)
    state = fields.Selection([
        ('draft', 'New'),
        ('waiting', 'Waiting Another Move'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'),
        ('assigned', 'Available'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='Status',
        readonly=True,)

    origin_qty = fields.Float('Origin Quantity')
    qty_orders = fields.Float(string='D S', help="Delivery SubOrder")
    quantity = fields.Float( string='Q S', readonly=False, help="Quantity SubOrder" )
    remaining_qty = fields.Float( string='R S ', help="Remaining SubOrder")
    upconsume_qty = fields.Float( string='Up C S ', help="Up Consume SubOrder")

    qty_orders_agreement = fields.Float( string='D A', help="Delivery Agreement")
    remaining_qty_agreement = fields.Float( string='R A ', help="Remaining Agreement")
    upconsume_qty_agreement = fields.Float(string='Up C A', help="Up Consume Agreement")

    def _query(self):
        return """
        SELECT mp.name as name ,mp.product_id as main_product_id, mp.date_start as date_start,mp.date_finished as date_finished,
		sm.product_id as sub_product_id, 
		sm.product_packaging_id as product_packaging_id,
		sm.location_id as location_id,
		sm.product_uom_qty as product_uom_qty,
		sm.quantity as quantity,
		sm.product_uom as product_uom,
		sm.picked as picked,
		sm.picking_type_id as picking_type_id,
		sm.location_dest_id as location_dest_id,
		sm.state as state,
		
		sm.origin_qty as origin_qty,
		sm.origin_qty as origin_qty,
		sm.qty_orders as qty_orders,
		sm.quantity as quantity,
		sm.remaining_qty as remaining_qty,
		sm.upconsume_qty as upconsume_qty,
		
		sm.qty_orders_agreement as qty_orders_agreement,
		sm.remaining_qty_agreement as remaining_qty_agreement,
		sm.upconsume_qty_agreement as upconsume_qty_agreement
		
                FROM stock_move sm inner join mrp_production mp on mp.id=sm.raw_material_production_id
            LIMIT 100
        """

    @property
    def _table_query(self):
        return self._query()
