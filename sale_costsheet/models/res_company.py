# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    retention_ap_default_product_id = fields.Many2one(
            comodel_name='product.product',
            string="Retention(AP) Product",
            help="Default product used for Rentention Account Payable",
            check_company=True,
        )

    advanced_ap_default_product_id = fields.Many2one(
            comodel_name='product.product',
            string="Advanced(AP) Product",
            help="Default product used for Advanced Account Payable",
            check_company=True,
        )
    insurance_ap_default_product_id= fields.Many2one(
            comodel_name='product.product',
            string="Insurance(AP) Product",
            help="Default product used for Insurance Account Payable",
            check_company=True,
        )

    retention_ar_default_product_id = fields.Many2one(
        comodel_name='product.product',
        string="Retention(AR) Product",
        help="Default product used for Rentention Account Receivable",
        check_company=True,
    )

    advanced_ar_default_product_id = fields.Many2one(
        comodel_name='product.product',
        string="Advanced(AR) Product",
        help="Default product used for Advanced Account Receivable",
        check_company=True,
    )
    insurance_ar_default_product_id = fields.Many2one(
        comodel_name='product.product',
        string="Insurance(AR) Product",
        help="Default product used for Insurance Account Receivable",
        check_company=True,
    )