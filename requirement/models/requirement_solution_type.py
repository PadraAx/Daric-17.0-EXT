from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class RequirementSolutionType(models.Model):
    _name = "requirement.solution.type"
    _description = "Solution Types"

    solution_type = fields.Selection(
        selection=[
            ("1", "Standard"),
            ("2", "Data Import"),
            ("3", "Development"),
            ("4", "Integration"),
            ("5", "Community app"),
        ],
        string='Solution Type')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner')
    sequence = fields.Integer(string='Sequence')
   