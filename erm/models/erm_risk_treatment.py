from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class ERMRiskTreatment(models.Model):
    _name = "erm.risk.treatment"
    _description = "Treatment"

    name = fields.Char(string='Title',required=True, readonly = False, store =True, index=False, copy=True,  tracking=False)
    description = fields.Text(string='Description')
    treatment_type = fields.Selection(selection=[
            ("1", "Treat"),
            ("2", "Terminate"),
            ("3", "Tolerate"),
            ("4", "Transfer"),
           
        ],
        string='Treatment Type', tracking=True , required=True)
    parent_id = fields.Many2one('erm.risk.assessment.analysis', string='Analysis')
    implementation_status = fields.Selection(selection=[
            ("1", "Planned"),
            ("2", "In Progress"),
            ("3", "Completed"),
        ],
        string='Implementation Status', tracking=True , required=True)
    effectiveness = fields.Float(string='Effectiveness (%)', compute='_compute_effectiveness')
    # risk_id = fields.Many2one('risk', string='Risk')
    escalated_to_id = fields.Many2one('res.users', string='Escalated To')
    escalation_needed = fields.Text(string='Escalation Needed')
    mitigation_action_plan_ids = fields.One2many('erm.mitigation.action.plan', 'parent_id', string='Mitigation Action Plans')
    treatment_start_date = fields.Date(string='Treatment Start Date')
    treatment_end_date = fields.Date(string='Treatment End Date')
    assessment_followup_date = fields.Date(string='Assessment Followup Date')
    cost = fields.Float(string='Cost', required=True)
    benefit = fields.Float(string='Benefit', required=True)
    ratio = fields.Float(string='Cost-Benefit Ratio', compute='_compute_ratio')

    @api.depends('cost', 'benefit')
    def _compute_ratio(self):
        for record in self:
            record.ratio = record.benefit / record.cost if record.cost else 0

    # comments = fields.Text(string='Comments')


    def _compute_effectiveness(self):
        self.effectiveness = 0
        # Compute effectiveness logic here
       
  
    
