# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import date
from odoo import models, fields, api


class Users(models.Model):
    _inherit = 'res.users'


    def get_request_access_record(self):
        show_request = self.env['knowledge.request'].search([]).filtered(lambda r: r.has_access)
        return [('id', 'in', show_request.ids)]
