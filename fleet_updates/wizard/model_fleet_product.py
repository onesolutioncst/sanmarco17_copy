# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from docxtpl import DocxTemplate
import num2words


class model_fleet_product(models.TransientModel):
    _name = "model.fleet.product"

    model_id = fields.Many2one('fleet.vehicle.model', 'Model')
    product_id = fields.Many2one('product.product')

    def create_product_fleet(self):
        if self.product_id.fleet_vehicle_id:
            self.product_id.fleet_vehicle_id.sudo().write(
                {'name': self.product_id.name, 'product_product_id': self.product_id.id, 'model_id': self.model_id.id})
        else:
            fleet_vehicle_obj = self.env['fleet.vehicle'].sudo().create(
                {'name': self.product_id.name, 'product_product_id': self.product_id.id, 'model_id': self.model_id.id})
            self.product_id.fleet_vehicle_id = fleet_vehicle_obj.id
        return True
