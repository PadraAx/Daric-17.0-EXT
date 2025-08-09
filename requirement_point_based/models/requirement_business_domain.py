from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class RequirementBusinessDomains(models.Model):
    _inherit = "requirement.business.domains"
   
 
    min_score = fields.Integer(string='Min score')
   
    _sql_constraints = [
        ('check_min_score', 'CHECK(min_score >= 0)', 'The Minimum score should be positive.'),
    ]
