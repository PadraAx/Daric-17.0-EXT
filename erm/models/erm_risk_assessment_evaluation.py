from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class ERMRiskAssessmentEvaluation(models.Model):
    _name = 'erm.risk.assessment.evaluation'
    _description = 'Risk Assessment Evaluation'

    type = fields.Selection([('erm.risk.impact', 'Severity/Impact'), ('erm.risk.likelihood', 'Probability/Likelihood')],
            string="Type",
            required=True)
    impact_ids = fields.One2many('erm.risk.impact', 'parent_id', string='Impact',)
    likelihood_ids = fields.One2many('erm.risk.likelihood', 'parent_id', string='Likelihood',) 
    inherent_risk  =fields.Reference(
            selection=[
                ('erm.risk.impact', 'Severity/Impact'),
                ('erm.risk.likelihood', 'Probability/Likelihood')
            ],
            string='Inherent Risk') 
    current_risk  = fields.Reference(
            selection=[
                ('erm.risk.impact', 'Severity/Impact'),
                ('erm.risk.likelihood', 'Probability/Likelihood')
            ],
            string='Current Risk') 
    residual_risk  = fields.Reference(
            selection=[
                ('erm.risk.impact', 'Severity/Impact'),
                ('erm.risk.likelihood', 'Probability/Likelihood')
            ],
            string= 'Residual Risk') 

    parent_id = fields.Many2one(
        'erm.risk.assessment', string='Risk Assessment')


    @api.onchange('type')
    def _onchange_type(self):
        for record in self:
            if record.type and record.type in self.env:
                # Fetch records from the selected model only
                record.inherent_risk = f"{record.type},1"
                record.current_risk = f"{record.type},1"
                record.residual_risk = f"{record.type},1"
            else:
                record.inherent_risk = None
                record.current_risk = None
                record.residual_risk = None

  