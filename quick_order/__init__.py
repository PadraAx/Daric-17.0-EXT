# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################

from . import controller
from . import model

def pre_init_check(cr):
    from odoo.release import series
    from odoo.exceptions import ValidationError

    if not('16.0' < series <= '17.0'):
        raise ValidationError('Module support Odoo series 17.0 found {}.'.format(series))
