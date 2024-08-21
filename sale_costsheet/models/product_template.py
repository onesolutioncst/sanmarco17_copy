from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"

class product_template(models.Model):
    _inherit = "product.template"

    is_discount = fields.Boolean('Is Discount')
    refundable = fields.Boolean('Is Refundable')
    subcontractor = fields.Boolean('Is Subcontractor')
    variation_Order = fields.Boolean('Is Variation Order')
    wages = fields.Boolean('Is Wages')
    supplier = fields.Boolean('Is Supplier')
    customer = fields.Boolean('Is Customer')
    costsheet = fields.Boolean('Is Costsheet')
    project_age = fields.Integer('Product Age')


# class product_product(models.Model):
#     _inherit = "product.product"
#
#     is_discount = fields.Boolean('Is Discount')
#     is_retention_ar = fields.Boolean('Is Retention AR')
#     is_retention_ap = fields.Boolean('Is Retention AP')
#     is_advanced_ar = fields.Boolean('Is Advanced AR')
#     is_advanced_ap = fields.Boolean('Is Advanced AP')
#     insurance = fields.Boolean('Is Insurance')
#     refundable = fields.Boolean('Is Refundable')
#     subcontractor = fields.Boolean('Is Subcontractor')
#     variation_Order = fields.Boolean('Is Variation Order')
#     wages = fields.Boolean('Is Wages')
#     supplier = fields.Boolean('Is Supplier')
#     customer = fields.Boolean('Is Customer')
#     costsheet = fields.Boolean('Is Costsheet')
