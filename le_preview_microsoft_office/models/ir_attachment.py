# -*- coding: utf-8 -*-
import urllib.parse
from odoo import api, fields, models, _

import logging

_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def get_office_preview_link(self):
        urls = []
        base_url = self.sudo().env["ir.config_parameter"].sudo().get_param("web.base.url")

        for attachment in self:
            attachment = attachment.sudo()

            attachment.public = True

            if not attachment.access_token:
                attachment.generate_access_token()

            base_url = attachment.env["ir.config_parameter"].sudo().get_param("web.base.url")
            url = f"{base_url}/web/content?id={attachment.id}&download=true&access_token-{attachment.access_token}"

            urls.append("https://view.officeapps.live.com/op/embed.aspx?src=" + urllib.parse.quote_plus(url))

        return urls
