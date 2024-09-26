from odoo import api, fields, models, _, Command

CATEGORY_SELECTION = [
    ('required', 'Required'),
    ('optional', 'Optional'),
    ('no', 'None')]


class approval_category(models.Model):
    """ Defines bills of material for a product or a product template """
    _inherit = 'approval.category'

    # @api.onchange('approval_type')
    # def _onchange_approval_type(self):
    #     res = super(approval_category, self)._onchange_approval_type()
    #     if self.approval_type == 'costsheet_suborder':
    #         self.has_analytic_distribution = 'required'
    #         self.has_picking_type_id = 'required'
    #         self.has_location_src_id = 'required'
    #         self.has_location_dest_id = 'required'
    #         self.has_product_id = 'required'
    #         self.has_product_qty = 'required'
    #     if self.approval_type == 'costsheet_agreement':
    #         self.has_vendor_id = 'required'

    approval_type = fields.Selection(selection_add=[('costsheet_suborder', 'CostSheet (Suborder)'),
                                                    ('costsheet_multi_suborder', 'CostSheet (Suborder)'),
                                                    ('costsheet_agreement', 'Costsheet (Agreement)')
                                                    ])
    has_analytic_distribution = fields.Selection(
        CATEGORY_SELECTION, string="Has Analytic Distribution",default="no")
    has_picking_type_id = fields.Selection(
        CATEGORY_SELECTION, string="Has Operation Type",
        help="Additional Operation Type that should be specified on the request.",default="no")
    has_location_src_id = fields.Selection(
        CATEGORY_SELECTION, string="Has Components Location",
        help="Additional Components Location that should be specified on the request.", default="no")
    has_location_dest_id = fields.Selection(
        CATEGORY_SELECTION, string="Has Finished Products Location",
        help="Additional Finished Products Location that should be specified on the request.", default="no")
    has_vendor_id = fields.Selection(
        CATEGORY_SELECTION, string="Has Vendor",
        help="Additional Vendor that should be specified on the request.", default="no")
    has_product_id = fields.Selection(
        CATEGORY_SELECTION, string="Has Product",
        help="Additional Product that should be specified on the request.", default="no")
    has_product_qty = fields.Selection(
        CATEGORY_SELECTION, string="Has Product QTY",
        help="Additional Product Qty that should be specified on the request.", default="no")

    has_analytic_account = fields.Selection(
        CATEGORY_SELECTION, string="Has Analytic account", default="no")
    has_costsheet_order = fields.Selection(CATEGORY_SELECTION, string="Has Costsheet", default="no")
    has_multi_costsheet_order = fields.Selection(CATEGORY_SELECTION, string="Has Multi Costsheet", default="no")
