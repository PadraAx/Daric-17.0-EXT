from odoo import api, fields, models,_

class ERMRiskObjective(models.Model):
    _name = "erm.risk.objective"
    _description = "Objects"
    
    name = fields.Char(string='Name', required='True')
    category_id = fields.Many2one('erm.risk.objective.category', 'Category')

   