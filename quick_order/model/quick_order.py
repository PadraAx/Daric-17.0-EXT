# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
import logging
import datetime
import re

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_log = logging.getLogger(__name__)
CLEANR = re.compile('<.*?>') 

class QuickOrderLine(models.Model):
    _name = 'quick.order.line'

    name = fields.Char(string="Name", compute='get_name')
    product_id = fields.Many2one(comodel_name = "product.product", string = "Products", required = True)
    quantity = fields.Integer(string="Quantity", default=1)
    quick_order_id = fields.Many2one(comodel_name = "quick.order", string = "Quick Order", ondelete="cascade")
    description = fields.Text(string="Description")

    def unlink(self):
        return super(QuickOrderLine, self).unlink()

    def get_name(self):
        for line in self:
            line.name = line.product_id.name

    @api.onchange('product_id')
    def change_product_id(self):
        return {
                'domain':{'product_id':[('website_published','=', True)]},
                }

    # @api.model
    def _get_product_price(self):
        product_id = self.product_id
        if product_id:
            prodtuct_value = product_id.product_tmpl_id._get_combination_info(product_id.product_template_attribute_value_ids, product_id.id)
            return prodtuct_value.get("price")*self.quantity
        return 0
    
    def _get_custom_value(self, attr_id, custum_value=False):
        description = re.sub(CLEANR, '', self.description).split('.')
        description.pop(-1)
        attribute = self.env['product.attribute.value'].browse(attr_id).display_name
        for i in description:
            if i != '' and attribute in i:
                custum_value = i.split(attribute+': ')[1]
        return custum_value


class QuickOrder(models.Model):
    _name = "quick.order"
    name = fields.Char(string = "Name", readonly=True)
    website_id = fields.Many2one('website', string="website", ondelete='cascade')
    quick_order_line = fields.One2many(string="Quick Order Line",comodel_name="quick.order.line", inverse_name="quick_order_id")
    user_id=fields.Many2one(comodel_name="res.users", string="User", default=lambda self: self._uid, readonly=True )
    state = fields.Selection([('draft', 'Draft'),('shopping_list', 'Shopping List'),('done', 'Done')], string = "Order State", default = 'draft')
    create_date = fields.Date(string="Created Date")
    write_date = fields.Date(string="Updated Date")


    @api.model
    def create(self, vals):
        values,website = vals.get("quick_order_line"),vals.get("website_id")
        if not website:
            website = (self.env['website'].get_current_website()).id
        vals['website_id'] = website
        if values:
            invalid = list(map(lambda x: self.get_product_id(x), values))
            if invalid and (sorted(invalid) != sorted(list(set(invalid)))):
                raise ValidationError(_('There is a product have already exits in your Quick Order. Please update the existing one or delete'))
        result = super(QuickOrder, self).create(vals)
        postfix = str(result.id)
        exists = False
        if vals.get("state") == "draft":
            exists = self.search([('user_id', '=', vals.get('user_id')), ('website_id', '=', website), ('state', '=', 'draft'), ('id', '!=', result.id)], limit=1)
        if exists and exists.exists():
            raise ValidationError(_('There is already Quotation order %s in draft state for this customer. You can not create another draft qucik order for this customer. Please update the exixting one' % exists.name))
        if not vals.get('name'):
            name = False
            if len(postfix) == 1:
                name = 'QO00'+postfix
            elif len(postfix) == 2:
                name = 'QO0'+postfix
            else:
                name = 'QO'+postfix
            result.name = name
        quick_order = self.search([('state', '=', 'draft'), ('website_id', '=', website), ('user_id', '=', self._uid)])
        if len(quick_order) > 1:
            result.state = 'shopping_list'

        return result

    def write(self, vals):
        values = vals.get("quick_order_line")
        if values:
            invalid = list(filter(lambda a: a not in [False, None], list(map(lambda x: self.get_product_id(x), values))))
            check = any(x in invalid for x in self.quick_order_line.mapped("product_id.id"))
            if check or (invalid and (sorted(invalid) != sorted(list(set(invalid))))):
                raise ValidationError(_('There is a product have already exits in your Quick Order. Please update the existing one or delete'))
        result = super(QuickOrder, self).write(vals)
        return result


    def get_product_id(self, x):
        for i in x:
            if type(i).__name__ == "dict":
                return i.get("product_id")
