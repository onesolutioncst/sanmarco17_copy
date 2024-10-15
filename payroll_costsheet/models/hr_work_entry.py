from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging
_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class hr_work_entry_type(models.Model):
    _inherit = "hr.work.entry.type"

    product_id = fields.Many2one('product.product')

    def write(self, vals):
        if 'product_id' in vals and vals.get('product_id'):
            product_objs = self.env['product.product'].sudo().browse(vals['product_id'])
            product_objs.hr_work_entry_type_id = self.id
        return super(hr_work_entry_type, self).write(vals)