from odoo import api, fields, models,_

class ERMRiskTag(models.Model):
    _name = "erm.risk.tag"
    _description = "Risk Tags"
    
    name = fields.Char(string='Name', required='True')
    active = fields.Boolean(string="Active", default=True)
    color = fields.Integer(string="Color")

    _sql_constraints = [
        ('uniq_tag_name', 'unique(name,active)', 'Name must be unique'),
    ]