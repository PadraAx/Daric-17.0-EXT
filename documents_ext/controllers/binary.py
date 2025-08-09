# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import functools
import io
import json
import logging
import os
import unicodedata

try:
    from werkzeug.utils import send_file
except ImportError:
    from odoo.tools._vendor.send_file import send_file

import odoo
import odoo.modules.registry
from odoo import SUPERUSER_ID, _, http
from odoo.addons.base.models.assetsbundle import ANY_UNIQUE
from odoo.exceptions import AccessError, UserError
from odoo.http import request, Response
from odoo.tools import file_open, file_path, replace_exceptions
from odoo.tools.image import image_guess_size_from_field_name
from odoo.tools.mimetypes import guess_mimetype

from odoo.addons.web.controllers.binary import Binary


_logger = logging.getLogger(__name__)

BAD_X_SENDFILE_ERROR = """\
Odoo is running with --x-sendfile but is receiving /web/filestore requests.

With --x-sendfile enabled, NGINX should be serving the
/web/filestore route, however Odoo is receiving the
request.

This usually indicates that NGINX is badly configured,
please make sure the /web/filestore location block exists
in your configuration file and that it is similar to:

    location /web/filestore {{
        internal;
        alias {data_dir}/filestore;
    }}
"""


def clean(name):
    return name.replace('\x3c', '')


class CustomBinary(Binary):


    @http.route(['/web/content',
        '/web/content/<string:xmlid>',
        '/web/content/<string:xmlid>/<string:filename>',
        '/web/content/<int:id>',
        '/web/content/<int:id>/<string:filename>',
        '/web/content/<string:model>/<int:id>/<string:field>',
        '/web/content/<string:model>/<int:id>/<string:field>/<string:filename>'], type='http', auth="user")
    # pylint: disable=redefined-builtin,invalid-name
    def content_common(self, xmlid=None, model='ir.attachment', id=None, field='raw',
                       filename=None, filename_field='name', mimetype=None, unique=False,
                       download=False, access_token=None, nocache=False):
        with replace_exceptions(UserError, by=request.not_found()):
            record = request.env['ir.binary']._find_record(xmlid, model, id and int(id), access_token)
            stream = request.env['ir.binary']._get_stream_from(record, field, filename, filename_field, mimetype)
        send_file_kwargs = {'as_attachment': download}
        if unique:
            send_file_kwargs['immutable'] = True
            send_file_kwargs['max_age'] = http.STATIC_CACHE_LONG
        if nocache:
            send_file_kwargs['max_age'] = None

        res = stream.get_response(**send_file_kwargs)
        res.headers['Content-Security-Policy'] = "default-src 'none'"
        return res

    