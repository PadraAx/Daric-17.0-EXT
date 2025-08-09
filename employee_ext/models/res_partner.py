# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class Partner(models.Model):
    _inherit = 'res.partner'
    
    
    is_location = fields.Boolean('Is Location', default=False)

