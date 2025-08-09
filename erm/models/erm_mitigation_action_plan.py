from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class ERMMitigationActionPlan(models.Model):
    _name = 'erm.mitigation.action.plan'
    _description = 'Mitigation Action Plan'

    name = fields.Char(string='Action Name', required=True)
    description = fields.Text(string='Action Description')
    due_date = fields.Date(string='Due Date')
    revised_due_date  = fields.Date(string='Revised Due Date')
    status = fields.Selection([
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')],
        string='Status', required=True, default='planned')
    action_owner_id = fields.Many2one('res.users', string='Action Owner')
    parent_id = fields.Many2one(
        'erm.risk.treatment', string='Treatment')
