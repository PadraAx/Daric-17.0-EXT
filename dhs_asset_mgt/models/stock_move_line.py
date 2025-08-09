from odoo import models, fields, api
from collections import defaultdict
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.tools.misc import clean_context, OrderedSet, groupby


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.depends('product_id', 'quant_id')
    def _compute_price(self):
        for record in self:
            if record.quant_id:
                record.price = record.quant_id.price
            else:
                record.price = record.product_id.standard_price

    # @api.constrains('product_id', 'lot_id')
    # def _compute_lot_name(self):Lenovo All in one i7/16GB/512
    #     for record in self:
    #         if record.product_id.tracking == 'lot' and record.lot_id:
    #             sequence = self.env['ir.sequence'].next_by_code('stock.lot_name')
    #             record.lot_name = f'{record.product_id.name}-{sequence}'

    lot_name = fields.Char('Lot/Serial Number Name', store=True, compute=False)
    currency_id = fields.Many2one(related='product_id.currency_id')
    price = fields.Monetary('Price', copy=False, store=True, compute='_compute_price', readonly=False)

    def _synchronize_quant(self, quantity, location, action="available", in_date=False, **quants_value):
        """ quantity should be express in product's UoM"""
        lot = quants_value.get('lot', self.lot_id)
        package = quants_value.get('package', self.package_id)
        owner = quants_value.get('owner', self.owner_id)
        available_qty = 0
        if self.product_id.type != 'product' or float_is_zero(quantity, precision_rounding=self.product_uom_id.rounding):
            return 0, False
        if action == "available":
            # override to handel quant price
            available_qty, in_date = self.env['stock.quant']._update_available_quantity(
                self.product_id, location, quantity, lot_id=lot, package_id=package, owner_id=owner, in_date=in_date, price=self.price)
        elif action == "reserved" and not self.move_id._should_bypass_reservation():
            self.env['stock.quant']._update_reserved_quantity(
                self.product_id, location, quantity, lot_id=lot, package_id=package, owner_id=owner)
        if available_qty < 0 and lot:
            # see if we can compensate the negative quants with some untracked quants
            untracked_qty = self.env['stock.quant']._get_available_quantity(
                self.product_id, location, lot_id=False, package_id=package, owner_id=owner, strict=True)
            if not untracked_qty:
                return available_qty, in_date
            taken_from_untracked_qty = min(untracked_qty, abs(quantity))
            self.env['stock.quant']._update_available_quantity(
                self.product_id, location, -taken_from_untracked_qty, lot_id=False, package_id=package, owner_id=owner, in_date=in_date)
            self.env['stock.quant']._update_available_quantity(
                self.product_id, location, taken_from_untracked_qty, lot_id=lot, package_id=package, owner_id=owner, in_date=in_date)
        return available_qty, in_date

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for record in res:
            if record.product_id.tracking == 'lot' and not (record.lot_id or record.lot_name):
                sequence = self.env['ir.sequence'].next_by_code('stock.lot_name')
                record.lot_name = f'{record.product_id.name}-{sequence}'
