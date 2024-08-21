from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class repair_order(models.Model):
    _inherit = 'repair.order'

    fleet_vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')
