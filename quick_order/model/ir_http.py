# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

import logging
from odoo import api, models

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super().session_info()
        return self._add_quick_order_view_session_info(result)

    def get_frontend_session_info(self):
        result = super().get_frontend_session_info()
        return self._add_quick_order_view_session_info(result)
    

    def _add_quick_order_view_session_info(self, session_info):
        lang = self.env['res.lang'].search([('code','=',self.env.lang)])
        session_info['lang_decimal_point'] = lang.decimal_point
        session_info['lang_thousands_sep'] = lang.thousands_sep
        session_info['lang_grouping'] = lang.grouping
        return session_info