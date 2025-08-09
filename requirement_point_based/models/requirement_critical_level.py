from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class RequirementCriticalLevel(models.Model):
    _inherit = "requirement.critical.level"
   
    critical_point = fields.Selection(
            selection=[
                ("1", "1"),
                ("2", "2"),
                ("3", "3"),
                ("4", "4"),
                ("5", "5"), 
                ("0", "0"),
                ("-1", "-1"), 
                ("-2", "-2"),
                ("-3", "-3"),
                ("-4", "-4"),
                ("-5", "-5"),
            ],
            string='Critical Point', required=True)

   
   