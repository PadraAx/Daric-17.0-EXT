# -*- coding: utf-8 -*-

import base64
import io
import json
import logging
import zipfile
from contextlib import ExitStack

from markupsafe import Markup
from werkzeug.exceptions import Forbidden

from odoo import Command, http
from odoo.exceptions import AccessError
from odoo.http import request, content_disposition
from odoo.tools.translate import _

from odoo.addons.documents.controllers.documents import ShareRoute

logger = logging.getLogger(__name__)


class CustomShareRoute(ShareRoute):

    # util methods #################################################################################

    @http.route(['/documents/image/<int:res_id>',
                 '/documents/image/<int:res_id>/<int:width>x<int:height>',
                 ], type='http', auth="user")
    def content_image(self, res_id=None, field='datas', share_id=None, width=0, height=0, crop=False, share_token=None, **kwargs):
        record = request.env['documents.document'].browse(int(res_id))
        if share_id:
            share = request.env['documents.share'].browse(int(share_id))
            record = share._get_documents_and_check_access(share_token, [int(res_id)], operation='read')
        if not record or not record.exists():
            raise request.not_found()

        return request.env['ir.binary']._get_image_stream_from(
            record, field, width=int(width), height=int(height), crop=crop
        ).get_response()

    @http.route(["/document/download/all/<int:share_id>/<access_token>"], type='http', auth='user')
    def share_download_all(self, access_token=None, share_id=None):
        """
        :param share_id: id of the share, the name of the share will be the name of the zip file share.
        :param access_token: share access token
        :returns the http response for a zip file if the token and the ID are valid.
        """
        env = request.env
        try:
            share = env['documents.share'].browse(share_id)
            documents = share._get_documents_and_check_access(access_token, operation='read')
            if not documents:
                raise request.not_found()
            streams = (
                self._get_share_zip_data_stream(share, document)
                for document in documents
            )
            return self._generate_zip((share.name or 'unnamed-link') + '.zip', streams)
        except Exception:
            logger.exception("Failed to zip share link id: %s" % share_id)
        raise request.not_found()

    @http.route([
        "/document/avatar/<int:share_id>/<access_token>",
        "/document/avatar/<int:share_id>/<access_token>/<document_id>",
    ], type='http', auth='user')
    def get_avatar(self, access_token=None, share_id=None, document_id=None):
        """
        :param share_id: id of the share.
        :param access_token: share access token
        :returns the picture of the share author for the front-end view.
        """
        try:
            env = request.env
            share = env['documents.share'].browse(share_id)
            if share._get_documents_and_check_access(access_token, document_ids=[], operation='read') is not False:
                if document_id:
                    user = env['documents.document'].browse(int(document_id)).owner_id
                    if not user:
                        return env['ir.binary']._placeholder()
                else:
                    user = share.create_uid
                return request.env['ir.binary']._get_stream_from(user, 'avatar_128').get_response()
            else:
                return request.not_found()
        except Exception:
            logger.exception("Failed to download portrait")
        return request.not_found()

    @http.route(["/document/thumbnail/<int:share_id>/<access_token>/<int:id>"],
                type='http', auth='user')
    def get_thumbnail(self, id=None, access_token=None, share_id=None):
        """
        :param id:  id of the document
        :param access_token: token of the share link
        :param share_id: id of the share link
        :return: the thumbnail of the document for the portal view.
        """
        try:
            thumbnail = self._get_file_response(id, share_id=share_id, share_token=access_token, field='thumbnail')
            return thumbnail
        except Exception:
            logger.exception("Failed to download thumbnail id: %s" % id)
        return request.not_found()

    # single file download route.
    @http.route(["/document/download/<int:share_id>/<access_token>/<int:document_id>"],
                type='http', auth='user')
    def download_one(self, document_id=None, access_token=None, share_id=None, preview=None, **kwargs):
        """
        used to download a single file from the portal multi-file page.

        :param id: id of the file
        :param access_token:  token of the share link
        :param share_id: id of the share link
        :return: a portal page to preview and download a single file.
        """
        try:
            document = self._get_file_response(document_id, share_id=share_id, share_token=access_token, field='raw', as_attachment=not bool(preview))
            return document or request.not_found()
        except Exception:
            logger.exception("Failed to download document %s" % id)

        return request.not_found()

    # Upload file(s) route.
    @http.route(["/document/upload/<int:share_id>/<token>/",
                 "/document/upload/<int:share_id>/<token>/<int:document_id>"],
                type='http', auth='user', methods=['POST'], csrf=False)
    def upload_attachment(self, share_id, token, document_id=None, **kwargs):
        """
        Allows user upload if provided with the right token and share_Link.

        :param share_id: id of the share.
        :param token: share access token.
        :param document_id: id of a document request to directly upload its content
        :return if files are uploaded, recalls the share portal with the updated content.
        """
        share = http.request.env['documents.share'].browse(share_id)
        if not share.can_upload or (not document_id and share.action != 'downloadupload'):
            return http.request.not_found()

        available_documents = share._get_documents_and_check_access(
            token, [document_id] if document_id else [], operation='write')
        folder = share.folder_id
        folder_id = folder.id or False
        button_text = share.name or _('Share link')
        chatter_message = Markup("""<b>%s</b> %s <br/>
                               <b>%s</b> %s <br/>
                               <a class="btn btn-primary" href="/web#id=%s&model=documents.share&view_type=form" target="_blank">
                                  <b>%s</b>
                               </a>
                             """) % (
                _("File uploaded by:"),
                http.request.env.user.name,
                _("Link created by:"),
                share.create_uid.name,
                share_id,
                button_text,
            )
        Documents = request.env['documents.document']
        if document_id and available_documents:
            if available_documents.type != 'empty':
                return http.request.not_found()
            try:
                max_upload_size = Documents.get_document_max_upload_limit()
                file = request.httprequest.files.getlist('requestFile')[0]
                data = file.read()
                if max_upload_size and (len(data) > int(max_upload_size)):
                    # TODO return error when converted to json
                    return logger.exception("File is too Large.")
                mimetype = file.content_type
                write_vals = {
                    'mimetype': mimetype,
                    'name': file.filename,
                    'type': 'binary',
                    'datas': base64.b64encode(data),
                }
            except Exception:
                logger.exception("Failed to read uploaded file")
            else:
                available_documents.write(write_vals)
                available_documents.message_post(body=chatter_message)
        elif not document_id and available_documents is not False:
            try:
                documents = self._create_uploaded_documents(request.httprequest.files.getlist('files'), share, folder)
            except Exception:
                logger.exception("Failed to upload document")
            else:
                for document in documents:
                    document.message_post(body=chatter_message)
                if share.activity_option:
                    documents.documents_set_activity(settings_record=share)
        else:
            return http.request.not_found()
        return Markup("""<script type='text/javascript'>
                    window.open("/document/share/%s/%s", "_self");
                </script>""") % (share_id, token)

    # Frontend portals #############################################################################

    # share portals route.
    @http.route(['/document/share/<int:share_id>/<token>'], type='http', auth='user')
    def share_portal(self, share_id=None, token=None):
        """
        Leads to a user portal displaying downloadable files for anyone with the token.

        :param share_id: id of the share link
        :param token: share access token
        """
        try:
            share = http.request.env['documents.share'].browse(share_id)
            available_documents = share._get_documents_and_check_access(token, operation='read')
            if available_documents is False:
                # if share._check_token(token):
                #     options = {
                #         'expiration_date': share.date_deadline,
                #         'author': share.create_uid.name,
                #     }
                #     return request.render('documents.not_available', options)
                # else:
                    return request.not_found()

            shareable_documents = available_documents.filtered(lambda r: r.type != 'url')
            options = {
                'name': share.name,
                'base_url': share.get_base_url(),
                'token': str(token),
                'upload': share.action == 'downloadupload',
                'share_id': str(share.id),
                'author': share.create_uid.name,
                'date_deadline': share.date_deadline,
                'document_ids': shareable_documents,
            }
            if len(shareable_documents) == 1 and shareable_documents.type == 'empty':
                return request.render("documents.document_request_page", options)
            elif share.type == 'domain':
                options.update(all_button='binary' in [document.type for document in shareable_documents],
                               request_upload=share.action == 'downloadupload')
                return request.render('documents.share_workspace_page', options)

            total_size = sum(document.file_size for document in shareable_documents)
            options.update(file_size=total_size, is_files_shared=True)
            return request.render("documents.share_files_page", options)
        except Exception:
            logger.exception("Failed to generate the multi file share portal")
        return request.not_found()
