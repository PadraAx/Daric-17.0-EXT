from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class ERMCostBenefitAnalysis(models.Model):
    _name = 'erm.cost.benefit.analysis'
    _description = 'Cost-Benefit Analysis'

    treatment_id = fields.Many2one('risk.treatment', string='Treatment', required=True)
    cost = fields.Float(string='Cost', required=True)
    benefit = fields.Float(string='Benefit', required=True)
    ratio = fields.Float(string='Cost-Benefit Ratio', compute='_compute_ratio')

    @api.depends('cost', 'benefit')
    def _compute_ratio(self):
        for record in self:
            record.ratio = record.benefit / record.cost if record.cost else 0
