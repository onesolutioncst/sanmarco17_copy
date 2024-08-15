# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    retention_ap_default_product_id = fields.Many2one(
        related='company_id.retention_ap_default_product_id',
        readonly=False,
    )
    advanced_ap_default_product_id = fields.Many2one(
        related='company_id.advanced_ap_default_product_id',
        readonly=False,
    )

    insurance_ap_default_product_id = fields.Many2one(
        related='company_id.insurance_ap_default_product_id',
        readonly=False,
    )

    retention_ar_default_product_id = fields.Many2one(
        related='company_id.retention_ar_default_product_id',
        readonly=False,
    )
    advanced_ar_default_product_id = fields.Many2one(
        related='company_id.advanced_ar_default_product_id',
        readonly=False,
    )

    insurance_ar_default_product_id = fields.Many2one(
        related='company_id.insurance_ar_default_product_id',
        readonly=False,
    )