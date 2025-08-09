from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class ERMRiskControl(models.Model):
    _name = "erm.risk.control"
    _description = "Risk Controls"

    
    @api.depends('control_type','control_Automation')
    def _compute_design_effectiveness(self):
        for record in self:
                if record.control_type and record.control_Automation:
                    if record.control_type == "1" and record.control_Automation =="2":
                        record.design_effectiveness = 1
                    elif record.control_type == "1" and record.control_Automation =="1":
                        record.design_effectiveness = 2
                    elif record.control_type == "2" and record.control_Automation =="2":
                        record.design_effectiveness = 3
                    elif record.control_type == "2" and record.control_Automation =="1":
                       record.design_effectiveness = 4
                else:
                    record.design_effectiveness = 0

    # @api.depends('risk_analysis_id.inherent_risk_rating','overall_control_rating')
    def _compute_residual_risk_rating(self):
        for record in self:
                # if record.risk_analysis_id.inherent_risk_rating and record.overall_control_rating:
                #     # if record.control_type == "1" and record.control_Automation =="2":
                #     #     record.design_effectiveness = 1
                #     # elif record.control_type == "1" and record.control_Automation =="1":
                #     #     record.design_effectiveness = 2
                #     # elif record.control_type == "2" and record.control_Automation =="2":
                #     #     record.design_effectiveness = 3
                #     # elif record.control_type == "2" and record.control_Automation =="1":
                #        record.design_effectiveness = "Moderate"
                # else:
                    record.residual_risk_rating = 0

    @api.depends('control_rating')
    def _compute_overall_control_rating(self):
        for record in self:
                if record.control_rating:
                    if record.control_rating <= 2:
                        record.overall_control_rating = "Adequate"
                    elif record.control_rating == 3:
                        record.overall_control_rating = "Partially Adequate"
                    elif record.control_rating > 3:
                        record.overall_control_rating = "Inadequate"
                else:
                    record.overall_control_rating = "N/A"
    
    name = fields.Char(string='Title',required=True, readonly = False, store =True)
    parent_id = fields.Many2one('erm.risk.assessment.analysis', string='Related Analysis')
    description = fields.Text(string='Existing Control Design Description')
    test_step = fields.Text(string='Test steps')
    design_effectiveness = fields.Integer('Design Effectiveness', compute='_compute_design_effectiveness',stored=True)
    operating_effectiveness = fields.Integer(string='Operating Effectiveness',required=True)
    control_rating = fields.Integer(string='Control Rating (Value)',required=True)
    # overall_control_rating = fields.Integer('Overall Control Rating', compute='_compute_overall_control_rating',stored=True)
    overall_control_rating = fields.Char('Overall Control Rating', compute='_compute_overall_control_rating',stored=True)
    residual_risk_rating = fields.Integer('Residual Risk Rating', compute='_compute_residual_risk_rating',stored=True)
    control_type = fields.Selection(selection=[
            ("1", "Preventive"),
            ("2", "Detective")],
        string='Control Type', tracking=True, required=True)
    control_status = fields.Selection(selection=[
            ("1", "Active"),
            ("2", "Inactive"),
           
        ],
        string='Current Existing', tracking=True)
    risk_analysis_id = fields.Many2one('erm.risk.assessment.analysis', 'Analysis')
    control_owner_id = fields.Many2one('res.users', 'Control Owner',required=True)
    documented = fields.Selection(selection=[
            ("1", "Yes"),
            ("2", "No"),
            ("3", "N/A"),
           
        ],
        string='Documented', tracking=True)
    control_Automation = fields.Selection(selection=[
            ("1", "Manual"),
            ("2", "Automated"),
            ("3", "N/A"),
           
        ],
        string='Control Automation', tracking=True , required=True)
    frequency = fields.Selection(selection=[
            ("1", "Annually"),
            ("2", "Quarterly"),
            ("3", "Monthly"),
            ("4", "Weekly"),
            ("5", "Transactional"),
            ("6", "Continuous"),
            ("7", "Daily"),
            ("8", "N/A"),  
        ],
        string='Frequency', tracking=True)

