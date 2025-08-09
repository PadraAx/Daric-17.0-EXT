from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class ERMRiskconsequence(models.Model):
    _name = "erm.risk.consequence"
    _description = "Risk Consequences"

    name = fields.Char(string='Title',required=True, readonly = False, store =True)
    min = fields.Integer(string='Min',required=True)
    max = fields.Integer(string='Max',required=True)
    color = fields.Char(string="Color")
   