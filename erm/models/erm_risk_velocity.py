from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class ERMRiskVelocity(models.Model):
    _name = "erm.risk.velocity"
    _description = "Risk Velocity"

    name = fields.Char(string='Title',required=True, readonly = False, store =True)
    value = fields.Integer(string='Value',required=True)
    description = fields.Text(string='Description')
    color = fields.Char(string="Color")