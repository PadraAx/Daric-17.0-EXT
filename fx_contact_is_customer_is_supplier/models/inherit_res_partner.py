from odoo import fields, models

class InheritResPartner(models.Model):
    _inherit = 'res.partner'

    is_a_customer = fields.Boolean(string="Is a Customer")
    is_a_vendor = fields.Boolean(string="Is a Vendor")
