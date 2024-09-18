from odoo import fields, models, api
from odoo.exceptions import ValidationError,UserError

class binary_downloads(models.TransientModel):
    '''
    Developer: Tarek Mohamed Ibrahim, 2018-12-13, Cairo

    Foster the download process by creating a transint table in which a binary is attached,
    and then downloaded via the web/contents controller
    This saves much space at the customer's side database to not used by unncessary data
    '''

    _name = 'binary.downloads'

    filename = fields.Char('File')
    content = fields.Binary('Contents')

    @api.model
    def get_download_url(self, filedata_dict={}, **filedata):
        if filedata.get('filename') and filedata.get('content'):
            pass
        else:
            if type(filedata_dict)==dict and filedata_dict.get('filename', False) and filedata_dict.get('content', False):
                filedata = filedata_dict
            else:
                raise ValueError('Not correct passed parameter, you have to pass a dictionary with two keys: filename and content, or to pass keyword areguments filename and content')

        download_this = self.create(filedata)
        file_url = "/web/content?model=binary.downloads&field=content&filename_field=filename&id=%s&download=true"%download_this.id
        return {
            'type': 'ir.actions.act_url',
            'url': file_url,
            'target': 'new'
        }
