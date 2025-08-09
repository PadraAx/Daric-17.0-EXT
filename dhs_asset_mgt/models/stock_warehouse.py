# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from collections import namedtuple

from odoo import _, _lt, api, fields, models
from odoo.exceptions import UserError



class Warehouse(models.Model):
    _inherit = "stock.warehouse"
    

    code = fields.Char('Short Name', required=True, size=10, help="Short name used to identify your warehouse")
    