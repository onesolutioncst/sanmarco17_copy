from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class repair_order(models.Model):
    _inherit = 'repair.order'

    maintenance_equipment_id = fields.Many2one('maintenance.equipment', 'Equipment', required=True)




