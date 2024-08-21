from odoo import models, fields, _, api
from odoo.exceptions import ValidationError
split_chr = '\\' if ':' in __file__ else '/'  # if ':' in file_name then I'm running on windows server
import mimetypes

class fleet_contract_template(models.Model):
    _name = 'fleet.contract.template'
    _description = 'Fleet Contract Template'
    _inherit = ['mail.thread']

    name = fields.Char('Name', track_visibility='onchange')
    template = fields.Binary('Template', track_visibility='onchange')
    template_filename = fields.Char('File Name', track_visibility='onchange')
    keywords = fields.Text('Keywords', track_visibility='onchange')
    active = fields.Boolean('Active', track_visibility='onchange', default=True)
    type = fields.Selection(string="Type",
                            selection=[('sale', 'Sale'), ('purchase', 'Purchase')], required=True, )


    @api.constrains('template_filename')
    def check_template_filename(self):
        for record in self:
            if record.template_filename:
                if mimetypes.guess_type(record.template_filename)[0] != 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                    raise ValidationError(_("Sorry only 'Docx' type supported"))