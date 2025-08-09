from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class ERMRiskTreatmentType(models.Model):
    _name = "erm.risk.treatment.type"
    _description = "Treatment Type"

    name = fields.Char(string='Title',required=True, readonly = False, store =True, index=False, copy=True,  tracking=False)
    description = fields.Text(string='Description')
    active = fields.Boolean(string="Active", default=True, copy=False)
