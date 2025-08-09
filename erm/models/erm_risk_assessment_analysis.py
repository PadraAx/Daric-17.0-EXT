from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class ERMRiskAssessmentAnalysis(models.Model):
    _name = "erm.risk.assessment.analysis"
    _description = "Risk Assessment Analysis"

    name = fields.Char(string='Title',required=True, readonly = False, store =True)
    comments = fields.Text(string='Comments')
    contributing_factors = fields.Selection(
        selection=[
            ("1", "Internal Factors"),
            ("2", "External Factors"),
            ("3", "Environmental Factors"),
            ("5", "Technological Factors"),
            ("6", "Stakeholder Factors"),
            ("7", "Project-Specific Factors"),
            ("8", "Legal and Ethical Factors"),
        ],
        string='Contributing Factors', tracking=True)
    parent_id = fields.Many2one(
        'erm.risk.assessment', string='Risk Assessment')
    control_ids = fields.One2many('erm.risk.control', 'parent_id', string='Controls')
    treatment_ids = fields.One2many('erm.risk.treatment', 'parent_id', string='Treatments')

