from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _compute_asset_ids(self):
        for obj in self:
            obj.asset_ids = self.env['asset.component'].sudo().search([('using_user', '=', obj.id)]).ids

    asset_ids = fields.One2many('asset.component', compute='_compute_asset_ids', readonly=False, string='Assets')
    location_ids = fields.One2many('stock.location', 'user_ids', string='Location')

    # def get_asset(self):
    #     return ['|', ('location_id.user_ids', 'in', [self.env.user.id]), ('using_user.id', '=', self.env.user.partner_id.id)]
