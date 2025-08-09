from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class ERMRiskobjectiveCategory(models.Model):
    _name = "erm.risk.objective.category"
    _description = "Risk Objective Category"

    name = fields.Char(string='Title',required=True, readonly = False, store =True, index=False, copy=True,  tracking=False)
    description = fields.Text(string='Description')

