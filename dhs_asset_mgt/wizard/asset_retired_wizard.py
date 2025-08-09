from odoo import _, api, fields, models
from datetime import datetime
from odoo.tools.float_utils import float_is_zero, float_round
from odoo.exceptions import UserError


class AssetRetiredWizard(models.TransientModel):
    _name = 'asset.retired.wizard'

    def get_location_domain(self):
        domain = [('scrap_location', '=', True), ('usage', '=', 'internal')]
        if not self.env.user.has_group('dhs_asset_mgt.group_it_asset_admin'):
            domain.append(('user_ids', 'in', self.env.user.id))
        return domain

    location_id = fields.Many2one('stock.location', string='Location',
                                  required=True,
                                  domain=get_location_domain)
    asset_id = fields.Many2one('asset.component', string='Asset', required=True)
    product_id = fields.Many2one(related='asset_id.product_id')
    company_id = fields.Many2one(related='asset_id.company_id')

    def action_asset_retired(self):
        fields = ['move_type', 'priority', 'scheduled_date', 'date', 'picking_type_id', 'user_id', 'is_locked']
        stock_packing_values = self.env['stock.picking'].sudo().with_context({
            'restricted_picking_type_code': 'incoming',
        }).default_get(fields)
        picking_type_id = self.sudo().env['stock.picking.type'].search([
            ('code', '=', 'incoming'),
            ('company_id', '=', self.env.user.company_id.id),
            ('warehouse_id', '=', self.location_id.warehouse_id.id), ], limit=1)
        customer_loc, supplier_loc = self.location_id.warehouse_id._get_partner_locations()
        stock_packing = self.sudo().env['stock.picking'].with_context({
            'restricted_picking_type_code': 'incoming',
        }).create([{
            **stock_packing_values,
            'partner_id': self.asset_id.using_user.id,
            'location_id': customer_loc.id,
            'location_dest_id': self.location_id.id,
            'origin': self.asset_id.asset_number,
            'picking_type_id': picking_type_id.id,
            'move_ids': [(0, 0, {
                'name': self.product_id.name,
                'product_id': self.product_id.id,
                'product_uom_qty': 1,
                'location_id': customer_loc.id,
                'location_dest_id': self.location_id.id,

            })]
        }])
        stock_packing.button_validate()
        # update asset
        self.sudo().asset_id.write({
            'item_product': stock_packing.id,
            'location_id': self.location_id.id,
            'state': 'retired',
            'using_user': False,
            'history_id': [(0, 0, {
                'asset_id': self.asset_id.id,
                'user_id': self.asset_id.using_user.id,
                'action': 'retired',
                'date': datetime.now(),
                'inventory_id': stock_packing.id,
                'description': f"{stock_packing.name} Returned to {self.location_id.name}"
            })]
        })
