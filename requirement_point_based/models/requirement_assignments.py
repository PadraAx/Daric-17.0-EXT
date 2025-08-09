from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class RequirementAssignments(models.Model):
    _inherit = "requirement.assignments"


    weight_factor = fields.Selection(
            selection=[
                ("1", "1"),
                ("2", "2"),
                ("3", "3"),
                ("4", "4"),
                ("5", "5"),
            ],
            string='Weighted Factor', default="1")