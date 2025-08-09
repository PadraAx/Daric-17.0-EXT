# -*- coding: utf-8 -*-
import base64
import io
import re
from ast import literal_eval
from collections import OrderedDict

import requests
from PyPDF2 import PdfFileReader
try:
    from PyPDF2.errors import PdfReadError
except ImportError:
    from PyPDF2.utils import PdfReadError
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv import expression
from odoo.tools import image_process
from odoo.tools.mimetypes import get_extension
from odoo.tools.misc import clean_context
from odoo.addons.mail.tools import link_preview

class Document(models.Model):
    _inherit = 'documents.document'
    
    def get_is_manager(self):
        for item in self:
            item.is_manager = False
            if item.folder_id:
                 item.is_manager = item.folder_id.has_write_access
          
    def _sanitize_file_extension(extension):
        """ Remove leading and trailing spacing + Remove leading "." """
        return re.sub(r'^[\s.]+|\s+$', '', extension) 
    def _sanitize_orginal_file_extension(extension):
        """ Remove leading and trailing spacing + Remove leading "." """
        return re.sub(r'^[\s.]+|\s+$', '', extension) 
       
    is_manager = fields.Boolean(string="is_manager", compute="get_is_manager")
    file_extension = fields.Char('File Extension', copy=True, store=True, readonly=False,
                                 compute='_compute_file_extension', inverse='_inverse_file_extension')
    document_orginal_file_id = fields.Many2one('documents.document', string='Orginal', tracking=True )
    tag_ids = fields.Many2many('documents.tag', 'document_tag_rel', string="Tags", tracking=True)
#    ////////////////////////////////////////////////////////////

  # Attachment
    orginal_attachment_id = fields.Many2one('ir.attachment', ondelete='cascade', auto_join=True, copy=False)
    orginal_attachment_name = fields.Char('Orginal Attachment Name', related='orginal_attachment_id.name', readonly=False)
    orginal_attachment_type = fields.Selection(string='Orginal Attachment Type', related='orginal_attachment_id.type', readonly=False)
    orginal_is_editable_attachment = fields.Boolean(default=False, help='True if we can edit the link attachment.')
    orginal_is_multipage = fields.Boolean('Is considered multipage', compute='_compute_orginal_is_multipage', store=True)
    orginal_datas = fields.Binary(related='orginal_attachment_id.datas', related_sudo=True, readonly=False, prefetch=False)
    orginal_raw = fields.Binary(related='orginal_attachment_id.raw', related_sudo=True, readonly=False, prefetch=False)
    orginal_file_extension = fields.Char('Orginal File Extension', copy=True, store=True, readonly=False,
                                 compute='_compute_orginal_file_extension', inverse='_inverse_orginal_file_extension')
    orginal_file_size = fields.Integer(related='orginal_attachment_id.file_size', store=True)
    orginal_checksum = fields.Char(related='orginal_attachment_id.checksum')
    orginal_mimetype = fields.Char(related='orginal_attachment_id.mimetype')
    orginal_res_model = fields.Char('Orginal Resource Model', compute="_compute_orginal_res_record", inverse="_inverse_orginal_res_model", store=True)
    orginal_res_id = fields.Many2oneReference('Orginal Resource ID', compute="_compute_orginal_res_record", inverse="_inverse_orginal_res_model", store=True, model_field="orginal_res_model")
    orginal_res_name = fields.Char('Orginal Resource Name', compute="_compute_orginal_res_name", compute_sudo=True)
    orginal_index_content = fields.Text(related='orginal_attachment_id.index_content')
    orginal_description = fields.Text('Orginal Attachment Description', related='orginal_attachment_id.description', readonly=False)
    orginal_url = fields.Char('Orginal URL', index=True, size=1024, tracking=True)
    orginal_url_preview_image = fields.Char('Orginal URL Preview Image', store=True, compute='_compute_orginal_name_and_preview')
     # Published Versioning
    previous_attachment_ids = fields.Many2many(comodel_name="ir.attachment", 
                                    relation="m2m_ir_document_previous_attachment_rel", 
                                    string="Orginal History")
    # Orginal Versioning
    orginal_previous_attachment_ids= fields.Many2many(comodel_name="ir.attachment", 
                                    relation="m2m_ir_document_orginal_previous_attachments_rel", 
                                    string="Orginal History")
    # Document
    orginal_name = fields.Char('Orginal Name', copy=True, store=True, compute='_compute_orginal_name_and_preview', inverse='_inverse_orginal_name')
    orginal_thumbnail = fields.Binary(readonly=False, store=True, attachment=True, compute='_compute_orginal_thumbnail')
    orginal_thumbnail_status = fields.Selection([
            ('present', 'Present'), # Document has a thumbnail
            ('error', 'Error'), # Error when generating the thumbnail
        ], compute="_compute_orginal_thumbnail_status", store=True, readonly=False,
    )
 
    orginal_type = fields.Selection([('url', 'URL'), ('binary', 'File'), ('empty', 'Request')],
                            string='Orginal Type', required=True, store=True, default='empty', change_default=True,
                            compute='_compute_orginal_type')
  



    _sql_constraints = [
        ('orginal_attachment_unique', 'unique (orginal_attachment_id)', "This attachment is already a document"),
    ]

# /////////////////////////////////////////////////////////////////


    @api.depends('orginal_name', 'orginal_type')
    def _compute_orginal_file_extension(self):
        for record in self:
            if record.orginal_type != 'binary':
                record.orginal_file_extension = False
            elif not record.orginal_file_extension and record.orginal_name:
                record.orginal_file_extension = Document._sanitize_orginal_file_extension(get_extension(record.orginal_name.strip())) or False

    def _inverse_orginal_file_extension(self):
        for record in self:
            record.orginal_file_extension = Document._sanitize_orginal_file_extension(record.orginal_file_extension) if record.orginal_file_extension else False

    @api.depends('orginal_attachment_id', 'orginal_attachment_id.name', 'orginal_url')
    def _compute_orginal_name_and_preview(self):
        request_session = requests.Session()
        for record in self:
            if record.orginal_attachment_id:
                record.orginal_name = record.orginal_attachment_id.name
                record.orginal_url_preview_image = False
            elif record.orginal_url:
                preview = link_preview.get_link_preview_from_url(record.orginal_url, request_session)
                if not preview:
                    continue
                if preview.get('og_title'):
                    record.orginal_name = preview['og_title']
                if preview.get('og_image'):
                    record.orginal_url_preview_image = preview['og_image']

    def _inverse_orginal_name(self):
        for record in self:
            if record.orginal_attachment_id:
                record.orginal_attachment_name = record.orginal_name

    @api.depends('orginal_datas', 'orginal_mimetype')
    def _compute_orginal_is_multipage(self):
        for document in self:
            # external computation to be extended
            document.orginal_is_multipage = bool(document._get_orginal_is_multipage())  # None => False

    @api.depends('orginal_attachment_id', 'orginal_attachment_id.res_model', 'orginal_attachment_id.res_id')
    def _compute_orginal_res_record(self):
        for record in self:
            attachment = record.orginal_attachment_id
            if attachment:
                record.orginal_res_model = attachment.res_model
                record.orginal_res_id = attachment.res_id

    @api.depends('orginal_attachment_id', 'orginal_res_model', 'orginal_res_id')
    def _compute_orginal_res_name(self):
        for record in self:
            if record.orginal_attachment_id:
                record.orginal_res_name = record.orginal_attachment_id.res_name
            elif record.orginal_res_id and record.orginal_res_model:
                record.orginal_res_name = self.env[record.orginal_res_model].browse(record.orginal_res_id).display_name
            else:
                record.orginal_res_name = False

    def _inverse_orginal_res_model(self):
        for record in self:
            attachment = record.orginal_attachment_id.with_context(no_document=True)
            if attachment:
                # Avoid inconsistency in the data, write both at the same time.
                # In case a check_access is done between orginal_res_id and orginal_res_model modification,
                # an access error can be received. (Mail causes this check_access)
                attachment.sudo().write({'res_model': record.orginal_res_model, 'res_id': record.orginal_res_id})

    @api.depends('orginal_checksum')
    def _compute_orginal_thumbnail(self):
        for record in self:
            if record.orginal_mimetype == 'application/pdf':
                # Thumbnails of pdfs are generated by the client. To force the generation, we invalidate the thumbnail.
                record.orginal_thumbnail = False
            else:
                try:
                    record.orginal_thumbnail = base64.b64encode(image_process(record.orginal_raw, size=(200, 140), crop='center'))
                except (UserError, TypeError):
                    record.orginal_thumbnail = False

    @api.depends("orginal_thumbnail")
    def _compute_orginal_thumbnail_status(self):
        domain = [
            ('res_model', '=', self._name),
            ('res_field', '=', 'orginal_thumbnail'),
            ('res_id', 'in', self.ids),
        ]
        documents_with_orginal_thumbnail = set(res['res_id'] for res in self.env['ir.attachment'].sudo().search_read(domain, ['res_id']))
        for document in self:
            if document.orginal_mimetype == 'application/pdf':
                # As the orginal_thumbnail invalidation is not propagated to the status, we invalid it as well.
                document.orginal_thumbnail_status = False
            else:
                document.orginal_thumbnail_status = document.id in documents_with_orginal_thumbnail and 'present'

    @api.depends('orginal_attachment_type', 'orginal_url')
    def _compute_orginal_type(self):
        for record in self:
            record.orginal_type = 'empty'
            if record.orginal_attachment_id:
                record.orginal_type = 'binary'
            elif record.orginal_url:
                record.orginal_type = 'orginal_url'


    def _get_orginal_is_multipage(self):
        """
        :return: Whether the document can be considered multipage or `None` if unable determine
        :rtype: bool | None
        """
        if self.orginal_mimetype in ('application/pdf', 'application/pdf;base64'):
            stream = io.BytesIO(base64.b64decode(self.orginal_datas))
            try:
                return PdfFileReader(stream, strict=False).numPages > 1
            except (ValueError, PdfReadError, KeyError):
                # ValueError for known bug in PyPDF2 v.1.26 (details in commit message)
                # PdfReadError: Non-pdf attachment stored as pdf in accounting (details in commit message)
                # KeyError happens when the user uploads a corrupted pdf (details in commit message)
                pass



    @api.depends('orginal_res_model')
    def _compute_orginal_res_model_name(self):
        for record in self:
            if record.orginal_res_model:
                record.res_model_name = self.env['ir.model']._get(record.orginal_res_model).display_name
            else:
                record.res_model_name = False

    def action_open_current_form(self):
        """ Open the form view of the current record """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Current Record',
            'res_model': 'documents.document',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }
    
    @api.model_create_multi
    def create(self, vals_list):
        orginal_attachments = []
        for vals in vals_list:
            keys = [key for key in vals if
                    self._fields[key].related and self._fields[key].related.split('.')[0] == 'orginal_attachment_id']
            attachment_dict = {key: vals.pop(key) for key in keys if key in vals}
            attachment = self.env['ir.attachment'].browse(vals.get('orginal_attachment_id'))

            if attachment and attachment_dict:
                attachment.write(attachment_dict)
            elif attachment_dict:
                attachment_dict.setdefault('name', vals.get('name', 'unnamed'))
                # default_res_model and default_res_id will cause unique constraints to trigger.
                attachment = self.env['ir.attachment'].with_context(clean_context(self.env.context)).create(attachment_dict)
                vals['orginal_attachment_id'] = attachment.id
            orginal_attachments.append(attachment)
        documents = super(Document, self).create(vals_list)
        return documents

    def write(self, vals):
        if vals.get('folder_id') and not self.env.is_superuser():
            folder = self.env['documents.folder'].browse(vals.get('folder_id'))
            if not folder.has_write_access:
                raise AccessError(_("You don't have the right to move documents to that workspace."))

        orginal_attachment_id = vals.get('orginal_attachment_id')
        if orginal_attachment_id:
            self.ensure_one()
        for record in self:

            if record.orginal_type == 'empty' and ('orginal_datas' in vals or 'url' in vals):
                body = _("Document Request: %s Uploaded by: %s", record.orginal_name, self.env.user.name)
                record.with_context(no_document=True).message_post(body=body)

            if record.orginal_attachment_id:
                # versioning
                if orginal_attachment_id:
                    if orginal_attachment_id in record.orginal_previous_attachment_ids.ids:
                        record.orginal_previous_attachment_ids = [(3, orginal_attachment_id, False)]
                    record.orginal_previous_attachment_ids = [(4, record.orginal_attachment_id.id, False)]
                if 'orginal_datas' in vals:
                    old_attachment = record.orginal_attachment_id.with_context(no_document=True).copy()
                    # removes the link between the old attachment and the record.
                    old_attachment.write({
                        'res_model': 'documents.document',
                        'res_id': record.id,
                    })
                    record.orginal_previous_attachment_ids = [(4, old_attachment.id, False)]
            elif vals.get('orginal_datas') and not vals.get('orginal_attachment_id'):
                orginal_res_model = vals.get('orginal_res_model', record.orginal_res_model or 'documents.document')
                orginal_res_id = vals.get('orginal_res_id') if vals.get('orginal_res_model') else record.orginal_res_id if record.orginal_res_model else record.id
                if orginal_res_model and orginal_res_model != 'documents.document' and not self.env[orginal_res_model].browse(orginal_res_id).exists():
                    record.orginal_res_model = orginal_res_model = 'documents.document'
                    record.orginal_res_id = orginal_res_id = record.id
                attachment = self.env['ir.attachment'].with_context(no_document=True).create({
                    'name': vals.get('orginal_name', record.orginal_name),
                    'res_model': orginal_res_model,
                    'res_id': orginal_res_id
                })
                record.orginal_attachment_id = attachment.id
                record.with_context(no_document=True)._process_activities(attachment.id)
     
        write_result = super(Document, self).write(vals)

        return write_result


    def unlink(self):
        """Remove its folder when deleting a document to ensure we don't retain unnecessary folders in the database.

        If:
            - The folder is inactive
            - It isn't linked to any files
            - It has no child folders
        """
        removable_folders = self.folder_id.with_context({'active_test': False}).filtered(
            lambda folder: len(folder.document_ids) == 1
            and not folder.children_folder_ids
            and not folder.active
        )
        removable_attachments = self.filtered(lambda self: self.orginal_res_model != self._name).orginal_attachment_id
        res = super().unlink()
        if removable_attachments:
            removable_attachments.unlink()
        if removable_folders:
            removable_folders.unlink()
        return res

# /////////////////////////////////////////////////////////////////

    
    @api.depends('name', 'type')
    def _compute_file_extension(self):
        for record in self:
            if record.type != 'binary':
                record.file_extension = False
            elif record.name:
                record.file_extension = Document._sanitize_file_extension(get_extension(record.name.strip())) or False
   
   
                