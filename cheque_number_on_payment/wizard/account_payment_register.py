from odoo import models, fields, api


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    cheque_number = fields.Char(string="Cheque Number")
    cheque_image = fields.Binary(string="Cheque Image")

    def _create_payments(self):
        res = super(AccountPaymentRegister, self)._create_payments()
        res.cheque_number = self.cheque_number
        res.cheque_image = self.cheque_image
        return res
