from odoo import api, fields, models, _
from odoo.exceptions import AccessDenied, UserError, ValidationError

CATEGORY_SELECTION = [
    ('required', 'Required'),
    ('optional', 'Optional'),
    ('no', 'None')]

class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    approval_type = fields.Selection(selection_add=[('create_transfer', 'Create Transfer'),])
    has_operation_type = fields.Selection(
        CATEGORY_SELECTION, string="Has Operation Type", default="no", required=True,)
    has_analytic_account = fields.Selection(
        CATEGORY_SELECTION, string="Has Analytic account", default="no", required=True,)


    @api.constrains('approval_type')
    @api.onchange('approval_type')
    def _onchange_approval_purchase_argument(self):
        if self.approval_type == 'create_transfer':
            self.has_operation_type = 'required'
            self.has_analytic_account = 'required'


