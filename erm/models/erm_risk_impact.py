from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class ERMRiskImpact(models.Model):
    _name = "erm.risk.impact"
    _description = "Risk Impacts"

    name = fields.Char(string='Title',required=True, readonly = False, store =True)
    value = fields.Integer(string='Value',required=True)
    description = fields.Text(string='Description')
    color = fields.Char(string="Color")
    parent_id = fields.Many2one(
        'erm.risk.assessment.evaluation', string='Evaluation')