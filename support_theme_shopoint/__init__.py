# -*- coding: utf-8 -*-
# ################################################################################

#   Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
# ################################################################################
# from . import models
# from . import controllers

from odoo.exceptions import UserError
from odoo.service import common


def pre_init_check(env):
	version_info = common.exp_version()
	server_serie = version_info.get('server_serie')
	if not 16 < float(server_serie) <= 17:
		raise UserError(f'Module support Odoo series 17.0 found {server_serie}.')