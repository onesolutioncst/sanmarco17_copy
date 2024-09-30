from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class account_move(models.Model):
    _inherit = 'account.move'

    maintenance_equipment_id = fields.Many2one('maintenance.equipment', 'Equipment', required=True)


class sale_order(models.Model):
    _inherit = 'sale.order'

    maintenance_equipment_id = fields.Many2one('maintenance.equipment', 'Equipment', required=True)



class purchase_order(models.Model):
    _inherit = 'purchase.order'

    maintenance_equipment_id = fields.Many2one('maintenance.equipment', 'Equipment', required=True)


