# -*- coding: utf-8 -*-

from odoo import models, fields, api


class IrExports(models.Model):
    _inherit = "ir.exports"

    group_ids = fields.Many2many(comodel_name='res.groups', string='Groups')
    user_ids = fields.Many2many(comodel_name='res.users', string='Users')
                



class Users(models.Model):
    _inherit = 'res.users'

    def get_export_access_record(self):
        valid_export = self.env['ir.exports'].search([]).filtered(lambda r: (self.env.user.id in r.user_ids.ids) or (r.group_ids.ids and set(r.group_ids.ids).issubset(set(self.env.user.groups_id.ids))))
        return [('id', 'in', valid_export.ids)]
