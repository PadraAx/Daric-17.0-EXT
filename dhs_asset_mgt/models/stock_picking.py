# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import models, api, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _order = "priority desc, scheduled_date desc, id desc"

    def _default_picking_type_id(self):
        picking_type_code = self.env.context.get('restricted_picking_type_code')
        if picking_type_code:
            picking_types = self.env['stock.picking.type'].search([
                ('code', '=', picking_type_code),
                ('company_id', '=', self.env.company.id),
            ])
            return picking_types[:1].id

    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=True, readonly=True, index=True, store=True,
        compute='_compute_picking_type')

    @api.depends('location_id', 'location_dest_id')
    def _compute_picking_type(self):
        picking_type_code = self.env.context.get('restricted_picking_type_code')
        for record in self:
            if picking_type_code:
                domain = [
                    ('code', '=', picking_type_code),
                    ('company_id', '=', self.env.company.id),
                ]
                if picking_type_code == 'outgoing' and record.location_id:
                    domain.append(('warehouse_id', '=', record.location_id.warehouse_id.id))
                if picking_type_code == 'incoming' and record.location_dest_id:
                    domain.append(('warehouse_id', '=', record.location_dest_id.warehouse_id.id))
                picking_types = self.env['stock.picking.type'].search(domain)
                record.picking_type_id = picking_types[:1].id
