# -*- coding: utf-8 -*-

from ast import literal_eval

from odoo import models, fields, api, exceptions
from odoo.tools.translate import _
from odoo.tools import consteq
import urllib.parse

from odoo.osv import expression

import uuid


class DocumentShare(models.Model):
    _inherit = 'documents.share'
   
    @api.depends('access_token')
    def _compute_full_url(self):
        for record in self:
            count = 0
            preview = ""
            for doc in record.document_ids:
                if doc.file_extension =="pdf":
                      count += 1
                      if count > 1 :
                          preview += ','
                      preview += (f'{record.get_base_url()}/web/content/{doc.res_id}?filename={doc.res_name}&model=documents.document')
            if count > 0:
                record.full_url = preview
            elif count < 1:
                record.full_url = (f'{record.get_base_url()}/document/share/'
                               f'{record._origin.id or record.id}/{record.access_token}')
    def _get_documents_and_check_access(self, access_token, document_ids=None, operation='write'):
        """
        :param str access_token: the access_token to be checked with the share link access_token
        :param list[int] document_ids: limit to the list of documents to fetch and check from the share link.
        :param str operation: access right to check on documents (read/write).
        :return: Recordset[documents.document]: all the accessible requested documents
        False if it fails access checks: False always means "no access right", if there are no documents but
        the rights are valid, it still returns an empty recordset.
        """
        self.ensure_one()
        if not self._check_token(access_token):
            return False
        if self.state == 'expired':
            return False
        documents = self._get_documents(document_ids)
        if operation == 'write':
            return self._get_writable_documents(documents)
        elif operation == 'read':
             return self._get_readable_documents(documents)
        else:
            return documents
        
    def _get_readable_documents(self, documents):
        """
        :param documents:
        :return: the recordset of documents for which the create_uid has write access
        False only if no write right.
        """
        self.ensure_one()
        try:
            # checks the rights first in case of empty recordset
            documents.with_user(self.env.uid).check_access_rights('read')
        except exceptions.AccessError:
            return False
        return documents.with_user(self.env.uid)._filter_access_rules('read')
    
    def _get_writable_documents(self, documents):
        """

        :param documents:
        :return: the recordset of documents for which the create_uid has write access
        False only if no write right.
        """
        self.ensure_one()
        try:
            # checks the rights first in case of empty recordset
            documents.with_user(self.env.uid).check_access_rights('write')
        except exceptions.AccessError:
            return False
        return documents.with_user(self.env.uid)._filter_access_rules('write')
                

   