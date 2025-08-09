from odoo import _, api, fields, models
from datetime import datetime
from odoo.tools.float_utils import float_is_zero, float_round
from odoo.exceptions import UserError


class AssetReassignmentWizard(models.TransientModel):
    _name = 'asset.reassignment.wizard'

    asignee_id = fields.Many2one('res.partner', string='Asignee', required=True)
    asset_id = fields.Many2one('asset.component', string='Asset', required=True)
    product_id = fields.Many2one(related='asset_id.product_id')
    company_id = fields.Many2one(related='asset_id.company_id')

    def action_asset_reassignment(self):
        fields = ['move_type', 'priority', 'scheduled_date', 'date', 'picking_type_id', 'user_id', 'is_locked']
        stock_packing_values = self.env['stock.picking'].sudo().with_context({
            'restricted_picking_type_code': 'outgoing',
        }).default_get(fields)
        picking_type_id = self.sudo().env['stock.picking.type'].search([
            ('code', '=', 'outgoing'),
            ('company_id', '=', self.env.user.company_id.id),
            ('warehouse_id', '=', self.asset_id.location_id.warehouse_id.id), ], limit=1)
        customer_loc, supplier_loc = self.asset_id.location_id.warehouse_id._get_partner_locations()
        stock_packing = self.sudo().env['stock.picking'].with_context({
            'restricted_picking_type_code': 'outgoing',
        }).create([{
            **stock_packing_values,
            'partner_id': self.asignee_id.id,
            'location_id': self.asset_id.location_id.id,
            'origin': self.asset_id.asset_number,
            'picking_type_id': picking_type_id.id,
            'location_dest_id': customer_loc.id,
            'move_ids': [(0, 0, {
                'name': self.product_id.name,
                'product_id': self.product_id.id,
                'product_uom_qty': 1,
                'location_id': self.asset_id.location_id.id,
                'location_dest_id': customer_loc.id,
            })]
        }])
        stock_packing.button_validate()
        self.sudo().asset_id.write({
            'item_product': stock_packing.id,
            'using_user': self.asignee_id.id,
            'location_id': self.asset_id.location_id.id,
            'state': 'running',
            'history_id': [(0, 0, {
                'asset_id': self.asset_id.id,
                'assign_id': self.asignee_id.id,
                'user_id': self.env.user.partner_id.id,
                'action': 'reassigment',
                'date': datetime.now(),
                'inventory_id': stock_packing.id,
                'description': f"{stock_packing.name} Assign To {self.asignee_id.name}"
            })]
        })
