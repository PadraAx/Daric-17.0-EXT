from odoo import models, fields

class StockLocation(models.Model):
    _inherit = 'stock.location'

    user_ids = fields.Many2many('res.users', string='Users')
