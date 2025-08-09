import polib
from deep_translator import GoogleTranslator
import base64
import logging

from odoo import api, fields, models, _

from ..utils.common import SUPPORTED_LANGUAGES

_logger = logging.getLogger(__name__)


class PoFileTranslator(models.TransientModel):
    _name = 'po.file.translator'
    _description = 'PO File Translator'
    _rec_name = 'source_lang'

    data = fields.Binary(string='PO file', required=True, attachment=False, help="PO file to traslate (.po file)")
    new_data = fields.Binary(string='New PO file', attachment=False)
    filename = fields.Char('File Name', required=True)
    source_lang = fields.Selection(SUPPORTED_LANGUAGES, string='Source languages', default="en", required=True)
    target_lang = fields.Selection(SUPPORTED_LANGUAGES, string='Target languages', default="en", required=True)
    overwrite = fields.Boolean(string='Overwrite existing translations?', default=False,
                               help="If you enable this option, any existing translations in this file will be "
                                    "overwritten and replaced by new translations.")
    state = fields.Selection([('upload', 'upload'), ('download', 'download')], default='upload')

    def action_translate_po_file(self):
        if self.data:
            po = polib.pofile(base64.decodebytes(self.data).decode('utf-8'))
            for entry in po:
                if not entry.msgid or (entry.msgstr and not self.overwrite):
                    continue
                try:
                    translation = GoogleTranslator(source=self.source_lang, target=self.target_lang).translate(entry.msgid)
                    entry.msgstr = translation
                except Exception as e:
                    msg = "%s %s %s %s" % (_("Translation error. The key could not be translated. Key:"),
                                           entry.msgid, _("Error:"), e)
                    _logger.warning(msg)

            self.write({
                'state': 'download',
                'new_data': base64.b64encode(str(po).encode('utf-8')),
                'filename': "New_%s" % self.filename
            })
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'po.file.translator',
                'view_mode': 'form',
                'res_id': self.id,
                'views': [(False, 'form')],
                'target': 'new',
            }
