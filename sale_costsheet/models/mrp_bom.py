from odoo import api, fields, models, _, Command
class MrpBom(models.Model):
    """ Defines bills of material for a product or a product template """
    _inherit = 'mrp.bom'

    product_id = fields.Many2one(
        'product.product', 'Product Variant',
        check_company=True, index=True,
        domain="[('product_tmpl_id', '=', product_tmpl_id)]",
        help="If a product variant is defined the BOM is available only for this product.")
