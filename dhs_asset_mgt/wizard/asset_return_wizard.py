from odoo import _, api, fields, models
from datetime import datetime
from odoo.tools.float_utils import float_is_zero, float_round
from odoo.exceptions import UserError


class AssetReturnWizard(models.TransientModel):
    _name = 'asset.return.wizard'

    def get_location_domain(self):
        domain = [('return_location', '=', True), ('usage', '=', 'internal')]
        if not self.env.user.has_group('dhs_asset_mgt.group_it_asset_admin'):
            domain.append(('user_ids', 'in', self.env.user.id))
        return domain

    location_id = fields.Many2one('stock.location', string='Location',
                                  required=True,
                                  domain=get_location_domain)
    asset_id = fields.Many2one('asset.component', string='Asset', required=True)
    product_id = fields.Many2one(related='asset_id.product_id')
    company_id = fields.Many2one(related='asset_id.company_id')

    def action_asset_return(self):
        this = self.sudo()
        return_wizard = this.env['stock.return.picking'].create({
            'picking_id': this.asset_id.item_product.id,
        })
        return_wizard._compute_moves_locations()
        move_id = return_wizard.product_return_moves.filtered(
            lambda item: item.product_id.id == this.asset_id.product_id.id).move_id.id
        return_wizard.product_return_moves = [(5, 0, 0)]
        return_wizard.write({
            'location_id': this.location_id.id,
            'product_return_moves': [(0, 0, {
                'product_id': this.asset_id.product_id.id,
                'quantity': 1,
                'move_id': move_id,
            })], })
        result = return_wizard.create_returns()
        new_picking_id = this.env['stock.picking'].browse(result['res_id'])
        new_picking_id.write({'partner_id': this.asset_id.item_product.partner_id.id,
                              })
        new_picking_id.move_ids_without_package.write({'quantity': 1})
        new_picking_id.button_validate()
        this.sudo().asset_id.write({
            'item_product': new_picking_id.id,
            'location_id': this.location_id.id,
            'state': 'returned',
            'using_user': False,
            'history_id': [(0, 0, {
                'user_id': this.env.user.partner_id.id,
                'action': 'returned',
                'date': datetime.now(),
                'inventory_id': new_picking_id.id,
                'description': f"{new_picking_id.name} Returned to {self.location_id.name}"
            })]
        })
