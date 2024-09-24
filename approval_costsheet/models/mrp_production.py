from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

from odoo.addons.test_convert.tests.test_env import record

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class mrp_production(models.Model):
    _inherit = "mrp.production"
    approval_count = fields.Integer(compute="calc_approval_count")

    def calc_approval_count(self):
        for record in self:
            record.approval_count = self.env['approval.request'].sudo().search_count([('mrp_production_id', '=', record.id)])

    def action_view_approval(self):
        return {
            'name': _('Costsheet Approval'),
            'view_mode': 'tree,form',
            'res_model': 'approval.request',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('mrp_production_id', '=', self.id)],
            'context': {'default_mrp_production_id': self.id}
        }

    def action_create_approval(self):
        new_wizard = self.env['approval.costsheet.wizard'].sudo().create({'mrp_manufacture_id': self.id,})
        return {
            'name': _('Costsheet Approvals'),
            'view_mode': 'form',
            'res_model': 'approval.costsheet.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': new_wizard.id,
        }