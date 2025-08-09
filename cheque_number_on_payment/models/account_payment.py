from odoo import fields, models, api


class AccountPayment(models.Model):
    _inherit = "account.payment"

    cheque_number = fields.Char(string="Cheque Number")
    cheque_image = fields.Binary(string="Cheque Image")
