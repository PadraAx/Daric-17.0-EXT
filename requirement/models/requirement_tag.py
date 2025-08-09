from odoo import api, fields, models,_

class RequirementTag(models.Model):
    _name = "requirement.tag"
    _description = "Requirement Tag"
    
    name = fields.Char(string='Name', required='True')
    active = fields.Boolean(string="Active", default=True)
    color = fields.Integer(string="Color")

    _sql_constraints = [
        ('uniq_tag_name', 'unique(name,active)', 'Name must be unique'),
    ]