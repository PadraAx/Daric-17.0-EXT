
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.http import request


class AuditExlude(models.Model):
    _name = 'audit.log'
    _description = 'Audit Log'

    user_id = fields.Many2one("res.users", "User", required=True) # the user who make change
    old_value = fields.Text("old_value") # fields text
    new_value = fields.Text("new_value") # fields text
    date = fields.Datetime(
        "Datetime", default=lambda self: fields.Datetime.now()
    ) # modify date
    method = fields.Text("method", required=True) # create/ wirte / unlink
    model_id = fields.Many2one("ir.model", string="Model")# the user who make change # many2one res.model
    res_ids = fields.Text("res_id", required=True) # fields text
    ip_address = fields.Text("ip_address") # fields text
    user_Agent = fields.Text("user_Agent") # fields text


    @api.model
    def get_user_info(self):

        request_ = request if request else False
        httprequest_ = request_.httprequest if request_ else False

        user_data = {
            'user_id': self.env.user.id,
            'ip_address': httprequest_.remote_addr if httprequest_ else '',
            'user_Agent': httprequest_.headers.get('User-Agent') if httprequest_ else '',
        }
        return user_data

    def create_user_log(self, data):
        user_info = self.get_user_info()
        values = {**user_info, **data}
        self.create(values)