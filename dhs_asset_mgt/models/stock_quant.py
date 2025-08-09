from odoo import models, fields, api, _
from collections import defaultdict
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.tools.misc import clean_context, OrderedSet, groupby


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.depends('product_id', 'inventory_quantity_auto_apply')
    def get_product_info(self):
        for record in self:
            record.p_currency_id = record.product_id.currency_id.id
            record.total_amount = record.inventory_quantity_auto_apply * record.price

    p_currency_id = fields.Many2one('res.currency',
                                    compute="get_product_info", store=False,  groups=False)
    price = fields.Monetary('Price', readonly=True, currency_field="p_currency_id")
    total_amount = fields.Monetary('Total', readonly=True, compute="get_product_info",
                                   store=False, currency_field="p_currency_id")

    @api.model
    def _update_available_quantity(self, product_id, location_id, quantity=False,
                                   reserved_quantity=False, lot_id=None, package_id=None,
                                   owner_id=None, in_date=None, price=None):
        # ************************
        # override to handel price on create quant
        # ************************
        # ************************
        """ Increase or decrease `quantity` or 'reserved quantity' of a set of quants for a given set of
        product_id/location_id/lot_id/package_id/owner_id.

        :param product_id:
        :param location_id:
        :param quantity:
        :param lot_id:
        :param package_id:
        :param owner_id:
        :param datetime in_date: Should only be passed when calls to this method are done in
                                 order to move a quant. When creating a tracked quant, the
                                 current datetime will be used.
        :return: tuple (available_quantity, in_date as a datetime)
        """
        if not (quantity or reserved_quantity):
            raise ValidationError(_('Quantity or Reserved Quantity should be set.'))
        self = self.sudo()
        quants = self._gather(product_id, location_id, lot_id=lot_id,
                              package_id=package_id, owner_id=owner_id, strict=True)
        if lot_id and quantity > 0:
            quants = quants.filtered(lambda q: q.lot_id)

        if location_id.should_bypass_reservation():
            incoming_dates = []
        else:
            incoming_dates = [quant.in_date for quant in quants if quant.in_date and
                              float_compare(quant.quantity, 0, precision_rounding=quant.product_uom_id.rounding) > 0]
        if in_date:
            incoming_dates += [in_date]
        # If multiple incoming dates are available for a given lot_id/package_id/owner_id, we
        # consider only the oldest one as being relevant.
        if incoming_dates:
            in_date = min(incoming_dates)
        else:
            in_date = fields.Datetime.now()

        quant = None
        if quants:
            # see _acquire_one_job for explanations
            self._cr.execute("SELECT id FROM stock_quant WHERE id IN %s ORDER BY lot_id LIMIT 1 FOR NO KEY UPDATE SKIP LOCKED", [
                             tuple(quants.ids)])
            stock_quant_result = self._cr.fetchone()
            if stock_quant_result:
                quant = self.browse(stock_quant_result[0])

        if quant:
            vals = {'in_date': in_date}
            if quantity:
                vals['quantity'] = quant.quantity + quantity
            if reserved_quantity:
                vals['reserved_quantity'] = quant.reserved_quantity + reserved_quantity
            quant.write(vals)
        else:
            vals = {
                'product_id': product_id.id,
                'location_id': location_id.id,
                'lot_id': lot_id and lot_id.id,
                'package_id': package_id and package_id.id,
                'owner_id': owner_id and owner_id.id,
                'in_date': in_date,
                'price': price
            }
            if quantity:
                vals['quantity'] = quantity
            if reserved_quantity:
                vals['reserved_quantity'] = reserved_quantity
            self.create(vals)
        return self._get_available_quantity(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=False, allow_negative=True), in_date

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        for record in res:
            groub_by_domain = []
            for item in groupby:
                groub_by_domain.append((item, '=', record[item][0]))
            if groub_by_domain:
                local_records = self.search(groub_by_domain + domain)
                record['total_amount'] = sum(local_records.mapped('total_amount'))
                record['inventory_quantity_auto_apply'] = sum(local_records.mapped('inventory_quantity_auto_apply'))
        return res
