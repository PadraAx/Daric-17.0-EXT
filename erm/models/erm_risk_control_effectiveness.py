from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class ERMRiskControlEffectiveness(models.Model):
    _name = "erm.risk.control.effectiveness"
    _description = "Control Effectiveness"

    name = fields.Char(string='Title' ,required=True)
    score = fields.Integer(string='Value',required=True)
    description = fields.Text(string='Description')
    rating = fields.Selection(
        selection=[
            ("1", "Effective"),
            ("2", "Limited Improvement Needed"),
            ("3", "Significant Improvement Needed"),
            ("4", "Ineffective"),
            ("5", "Highly Ineffective"),
        ],
        string='Rating', tracking=True)
