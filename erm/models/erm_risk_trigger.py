from odoo import api, fields, models,_

class ERMRiskTrigger(models.Model):
    _name = "erm.risk.trigger"
    _description = "Risk Triggers"
    
    name = fields.Char(string='Name', required='True')
    

   