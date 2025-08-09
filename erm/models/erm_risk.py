from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo import http
from odoo.http import request

STATES = [
    ("1", "Draft"),
    ("2", "Assessment"),
]

class ERMRisk(models.Model):
    _name = "erm.risk"
    _description = "Risk Analysis"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # @api.depends('impact_id','likelihood_id')
    # def _compute_risk_score(self):
    #     for record in self:
    #         if record.impact_id and record.likelihood_id:
    #            record.risk_score = record.impact_id.value * record.likelihood_id.value
    #         else:
    #             record.risk_score = 0

    @api.depends('state')
    def _compute_has_write_access(self):
        for rec in self:
            rec.has_write_access = True

    @api.depends('direct_cost','indirect_cost')
    def _compute_total_impact(self):
        for record in self:
            if record.direct_cost and record.indirect_cost:
               record.total_impact = record.direct_cost + record.indirect_cost
            else:
                record.total_impact = 0

    def _compute_risk_mitigation_cost(self):
        for record in self:
            record.risk_mitigation_cost = 0

    @api.depends('current_impact_id','current_likelihood_id')
    def _compute_current_risk_score(self):
         for record in self:
            if record.current_impact_id and record.current_likelihood_id:
               record.current_risk_score = record.current_impact_id.value * record.current_likelihood_id.value
            else:
                record.current_risk_score = 0

    @api.depends('residual_impact_id','residual_likelihood_id')
    def _compute_residual_risk_score(self):
         for record in self:
            if record.residual_impact_id and record.residual_likelihood_id:
               record.residual_risk_score = record.residual_impact_id.value * record.residual_likelihood_id.value
            else:
                record.residual_risk_score = 0



    req_code = fields.Char(string='Code', required=False, readonly = True,)
    state = fields.Selection(
        selection=STATES,
        string='Stage', default="1",readonly=True , tracking=True)
    parent_id = fields.Many2one('erm.risk.template', string='Related Risk')
    tag_ids = fields.Many2many('erm.risk.tag', string='Tags',tracking=True)
    current_impact_id = fields.Many2one('erm.risk.impact', help="The extent of consequences if the risk occurs.", string='Impact (Severity)',)
    current_likelihood_id = fields.Many2one('erm.risk.likelihood', help="The chance of the risk occurring.",string='Likelihood (Probability)',) 
    current_risk_score =  fields.Integer('Current Risk', help="A composite measure of risk based on likelihood and impact.", compute='_compute_current_risk_score',stored=True,  readonly = True) 
    residual_impact_id = fields.Many2one('erm.risk.impact', help="The extent of consequences if the risk occurs.", string='Impact (Severity)',)
    residual_likelihood_id = fields.Many2one('erm.risk.likelihood', help="The chance of the risk occurring.",string='Likelihood (Probability)',)
    residual_risk_score =  fields.Integer('Residual Risk', help="A composite measure of risk based on likelihood and impact.", compute='_compute_residual_risk_score',stored=True,  readonly = True) 

    # inherent_risk_score = fields.Integer('Inherent Risk Score', compute='_compute_inherent_risk_score',stored=True)
    # risk_rating = fields.Integer('Risk Rating', compute='_compute_risk_rating',stored=True) 
    risk_score =  fields.Integer('Risk Score (Risk Level)', help="A composite measure of risk based on likelihood and impact.", compute='_compute_risk_score',stored=True,  readonly = True) 
    currency_id = fields.Many2one(string='Currency', related="category_id.currency_id", store=True, readonly = True)
    # category_type_id =  fields.Many2one(string='Category Type', related="category_id.category_type_id", store=True, readonly = True)
    trigger_id = fields.Many2one('erm.risk.trigger', 'trigger',  help="Events or conditions that signal the risk might occur." ,required=True)
    timeframe = fields.Selection([('0', 'Immediate'),
                                  ('1', 'Short-term'),
                                  ('2', 'Long-term'),],
                                 string='Timeframe (Proximity)', help="How soon the risk is likely to occur.", required=True)
    detection_difficulty = fields.Selection([('0', 'Low'),
                                  ('1', 'Easy (1)'),
                                  ('2', 'Moderate (3)'),
                                  ('3', 'Difficult (5)')],
                                 string='Detection Difficulty', help="How hard it is to identify or detect the risk before it occurs.")
    
    direct_cost = fields.Monetary(string="Direct Costs", required=True, currency_field='currency_id',
                                   help="Estimate direct costs (e.g., repair costs, lost revenue).")
    indirect_cost = fields.Monetary(string="Indirect Costs", required=True, currency_field='currency_id',
                                     help="Estimate indirect costs (e.g., brand damage, regulatory fines).")
    total_impact  = fields.Monetary(string="Total Impact", compute='_compute_total_impact', readonly = True, stored=True, currency_field='currency_id',
                                     help="Total Impact = Direct Costs + Indirect Costs.")
    risk_mitigation_cost  = fields.Monetary(string="Risk Mitigation Cost", compute='_compute_risk_mitigation_cost', readonly = True, stored=True, currency_field='currency_id',
                                             help="Cost to implement risk mitigation measures.")
    risk_velocity_id =  fields.Many2one('erm.risk.velocity', help="The speed at which a risk can materialize and impact the project.",string='Risk Velocity',) 
    confidence_level = fields.Selection([('1', 'Low Confidence (1)'),
                                         ('5', 'High Confidence (5)')],
                                 string='Confidence Level', help="Degree of confidence in risk data and assessments.")
    dependencies_ids = fields.One2many('erm.risk.dependency', 'risk_id',
                                       string='Dependencies', readonly=True)
    has_write_access = fields.Boolean('Has write access', compute="_compute_has_write_access", default=True, readonly=True )
    category_id = fields.Many2one(string='Category', related="parent_id.category_id",  help="The type or nature of the risk." ,readonly = True)
    # category_type_id =  fields.Many2one(string='Category Type', related="parent_id.category_id.category_type_id", store=True, readonly = True)
    affected_area_id = fields.Many2one(string='Affected Area',related="parent_id.affected_area_id", store=True, readonly = True,)

   
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            category_id = vals.get('category_id')
            if category_id:
                category = self.env['erm.risk.category'].browse(category_id)
                if 'req_code' not in vals:
                    seq_name = f'erm_risk.seq.{category.name}.{ category.id}'
                    sequence = self.env['ir.sequence'].sudo().search([('code', '=', seq_name)], limit=1)
                    if not sequence:
                            sequence = self.env['ir.sequence'].sudo().create({
                                'name': seq_name,
                                'code': seq_name,
                                'padding': '4',  # Adjust padding as needed
                                'implementation': 'standard',
                                'number_increment': '1',
                                'number_next': '0',
                            })
                    vals['req_code'] = f'{ category.code}-{sequence.next_by_code(seq_name)}'
        return super(ERMRisk, self).create(vals_list)
    


DEP_STATES = STATES + [('unknown', 'Unknown'),]

class ERMRiskDependency(models.Model):
    _name = "erm.risk.dependency"
    _description = "Risk dependency"

    # the dependency name
    name = fields.Char(index=True)
    # the module that depends on it
    risk_id = fields.Many2one('erm.risk', 'Module', ondelete='cascade')
    # the module corresponding to the dependency, and its status
    depend_id = fields.Many2one('erm.risk', 'Dependency',
                                 compute='_compute_depend', search='_search_depend')
    state = fields.Selection(DEP_STATES, string='Status', compute='_compute_state')
    dependency_level = fields.Selection([('0', 'None'),
                                         ('1', 'Low'),
                                         ('2', 'Medium'),
                                         ('3', 'High')],
                                 string='Dependency Level')

 

    @api.depends('name')
    def _compute_depend(self):
        # retrieve all modules corresponding to the dependency names
        ids = list(set(dep.id for dep in self))
        mods = self.env['erm.risk'].search([('id', 'in', ids)])

        # index modules by name, and assign dependencies
        name_mod = dict((mod.id, mod) for mod in mods)
        for dep in self:
            dep.depend_id = name_mod.get(dep.id)

    def _search_depend(self, operator, value):
        assert operator == 'in'
        modules = self.env['erm.risk'].browse(set(value))
        return [('id', 'in', modules.mapped('id'))]

    @api.depends('depend_id.state')
    def _compute_state(self):
        for dependency in self:
            dependency.state = dependency.depend_id.state or 'unknown'
