from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class RequirementSolution(models.Model):
    _name = "requirement.solution"
    _description = "Solution"

    solution_code = fields.Text()
    review_id = fields.Many2one(comodel_name='requirement.review', string='Review')
   
