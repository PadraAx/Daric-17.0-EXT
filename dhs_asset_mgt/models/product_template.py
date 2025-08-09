# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ProductBrand(models.Model):
    _name = "product.brand"
    _description = "Product Brand"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string='name', tracking=True, required=True)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_brand = fields.Many2one('product.brand', string='Brand', tracking=True)

    currency_id = fields.Many2one(
        'res.currency', 'Currency', compute=False, store=True, default=lambda self: self.env.company.currency_id.id)
    cost_currency_id = fields.Many2one(
        'res.currency', 'Cost Currency', compute="get_cost_currency_id", store=False)

    @api.depends('currency_id')
    def get_cost_currency_id(self):
        for record in self:
            record.cost_currency_id = record.currency_id

    @api.depends('taxes_id', 'list_price', 'currency_id')
    def _compute_tax_string(self):
        for record in self:
            record.tax_string = record._construct_tax_string(record.list_price)
