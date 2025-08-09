# -*- coding: utf-8 -*-
import json

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    admins_notification_ids = fields.Many2many('res.partner',string='Admins Notification')

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('dhs_asset_mgt.admins_notification_ids', self.admins_notification_ids.ids)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        value = params.get_param('dhs_asset_mgt.admins_notification_ids')
        res.update(
            admins_notification_ids= [(6,0, json.loads(value))]  if value else [],
        )
        return res
