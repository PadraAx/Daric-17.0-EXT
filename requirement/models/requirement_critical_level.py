from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class RequirementCriticalLevel(models.Model):
    _name = "requirement.critical.level"
    _description = "Critical Level"

    name = fields.Char(string='Title')
    description = fields.Text( string='Description')
    active_to_next_state = fields.Boolean(string="Activate to change status", default=False, copy=False, readonly=True)
    _sql_constraints = [
        ('uniq_name', 'unique(name)', 'Name must be unique'),
    ]
    def action_active_to_next_state(self):
        records = self.env['requirement.critical.level'].search([("active_to_next_state", "=", True)])
        records.write({'active_to_next_state': False})
        self.active_to_next_state = True
        