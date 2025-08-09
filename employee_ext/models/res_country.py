# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, tools
from odoo.tools.translate import _


class Country(models.Model):
    _inherit = 'res.country'
    _description = 'Country'


    local_name = fields.Char(string='Local Name')
    