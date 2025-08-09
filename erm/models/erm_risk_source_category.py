from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class ERMRiskSourceCategory(models.Model):
    _name = "erm.risk.source.category"
    _description = "Risk Source Categories"

    name = fields.Char(string='Title',required=True, )
    description = fields.Text(string='Description')
   