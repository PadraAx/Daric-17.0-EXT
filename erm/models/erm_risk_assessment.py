from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import math

class ERMRiskAssessment(models.Model):
    _name = "erm.risk.assessment"
    _description = "Risk Assessments"
    _rec_name = "assessment_code"

    # @api.depends('parent_id.state')
    def _compute_has_write_access(self):
        for rec in self:
            # rec.has_write_access = False
            # if rec.create_uid.id == self.env.uid and rec.parent_id.state == '2':
            #     group = self.env.ref('risk.group_bra_assessmenter')
            #     group_id = group.id
            #     assignement = self.env['risk.assignments'].search_count([('business_domain_id', '=', rec.parent_id.business_domain_id.id),
            #                                                       ('user_id', '=', rec.create_uid.id),
            #                                                       ('group_id', '=', group_id),
            #                                                       ('company_id', '=',  rec.parent_id.company_id.id),
            #                                                       ])
            #     if assignement> 0:
                    rec.has_write_access = True

    def _compute_is_manager(self):
        for rec in self:
            # rec.is_manager = False
            # if rec.user_has_groups('risk.group_bra_admin'):
                rec.is_manager = True                  

    @api.depends('evaluation_ids')
    def _compute_inherent_risk_score(self):
        for record in self:
            if record.evaluation_ids:
                # record.inherent_risk_score =math.prod(rec.inherent_risk.value for rec in record.evaluation_ids)
                record.inherent_risk_score =sum(rec.inherent_risk.value for rec in record.evaluation_ids)
                consequence = self.env['erm.risk.consequence'].search([
                                ('min', '<=', record.inherent_risk_score),
                                ('max', '>=', record.inherent_risk_score)
                            ], limit=1)
                record.inherent_consequence_id = consequence.id
            else:
                record.inherent_risk_score = 0
              

    @api.depends('evaluation_ids')
    def _compute_current_risk_score(self):
        for record in self:
            if record.evaluation_ids:
                record.current_risk_score = sum(rec.current_risk.value for rec in record.evaluation_ids)
                consequence = self.env['erm.risk.consequence'].search([
                                ('min', '<=', record.current_risk_score),
                                ('max', '>=', record.current_risk_score)
                            ], limit=1)
                record.current_consequence_id = consequence.id
            else:
                record.current_risk_score = 0
    @api.depends('evaluation_ids')
    def _compute_residual_risk_score(self):
       for record in self:
            if record.evaluation_ids:
                record.residual_risk_score = sum(rec.residual_risk.value for rec in record.evaluation_ids)
                consequence = self.env['erm.risk.consequence'].search([
                                ('min', '<=', record.residual_risk_score),
                                ('max', '>=', record.residual_risk_score)
                            ], limit=1)
                record.residual_consequence_id = consequence.id
            else:
                record.residual_risk_score = 0
 
    assessment_code =  fields.Text(string='Code')
    name = fields.Char(string='Title' ,required=True)
    comments = fields.Html(string='Comments')
    parent_id = fields.Many2one('erm.risk', string='Related Risk', required=True)
    tag_ids = fields.Many2many('erm.risk.tag', string='Tags',tracking=True)
    has_write_access = fields.Boolean('Has write access', compute="_compute_has_write_access", default=True, readonly=True )
    is_manager = fields.Boolean('Is manager', compute="_compute_is_manager",default=False, readonly=True)
    # category_id = fields.Many2one('erm.risk.category', 'Category',required=True)
    # category_type_id =  fields.Many2one(string='Category Type',
    #                                   related="category_id.category_type_id", store=True,readonly = True)
    # impact_id = fields.Many2one('erm.risk.impact', 'Impact',required=True)
    # likelihood_id = fields.Many2one('erm.risk.likelihood', 'Likelihood',required=True) 
    inherent_risk_score = fields.Integer('Inherent Risk Score', compute='_compute_inherent_risk_score',stored=True)
    current_risk_score = fields.Integer('Current Risk Score', compute='_compute_current_risk_score',stored=True)
    residual_risk_score = fields.Integer('Residual Risk Score', compute='_compute_residual_risk_score',stored=True)

    inherent_consequence_id =  fields.Many2one('erm.risk.consequence', 'Inherent Consequence', stored=False, readonly=True)
    current_consequence_id =  fields.Many2one('erm.risk.consequence', 'Current Consequence', stored=False, readonly=True)
    residual_consequence_id =  fields.Many2one('erm.risk.consequence', 'Residual Consequence', stored=False, readonly=True )

    inherent_consequence_color =  fields.Char(related="inherent_consequence_id.color", string='Inherent Consequence', stored=False, readonly=True)
    current_consequence_color =  fields.Char(related="current_consequence_id.color", string='Current Consequence', stored=False, readonly=True)
    residual_consequence_color =  fields.Char(related="residual_consequence_id.color", string='Residual Consequence', stored=False, readonly=True )

    risk_velocity = fields.Integer(string='Velocity')
    inherent_risk_rating = fields.Selection([('0', 'Low'),
                                  ('1', 'Moderate'),
                                  ('2', 'High'),
                                  ('3', 'Very High')],
                                 string='Inherent Risk Rating', readonly = True)
    
    evaluation_ids = fields.One2many('erm.risk.assessment.evaluation', 
            'parent_id', string='Evaluation')
    analysis_ids = fields.One2many('erm.risk.assessment.analysis', 
            'parent_id', string='Analysis')
    

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            parent_id = vals.get('parent_id') 
            if parent_id:
                parent_id = self.env['erm.risk'].browse(parent_id)
                if 'assessment_code' not in vals:
                    seq_name = f'erm_assessment.seq.{parent_id.name}.{ parent_id.id}'
                    sequence = self.env['ir.sequence'].sudo().search([('code', '=', seq_name)], limit=1)
                    if not sequence:
                            sequence = self.env['ir.sequence'].sudo().create({
                                'name': seq_name,
                                'code': seq_name,
                                'padding': '6',  # Adjust padding as needed
                                'implementation': 'standard', 
                                'number_increment': '1', 
                                'number_next': '0', 
                            })
                    vals['assessment_code'] = f'{ parent_id.req_code}-{sequence.next_by_code(seq_name)}'
                score = vals.get('inherent_risk_score')
                if score:
                    parent_id.inherent_risk_score = score
                    if score <= 5:
                        parent_id.inherent_risk_rating = '0'
                    elif score > 5 and score < 8:
                        parent_id.inherent_risk_rating = '1'
                    elif score > 8 and score < 9:
                        parent_id.inherent_risk_rating = '2'
                    elif score > 9:
                        parent_id.inherent_risk_rating = '3'
                category_id = vals.get('category_id')
                if category_id:
                        parent_id.category_id = category_id
        return  super(ERMRiskAssessment, self).create(vals_list)
    
    # def write(self, vals):
    #    if not self.ref and not vals.get('ref'):
    #    return super(ermRiskAssessment, self).write(vals)   
    def open_action(self):
        return {
            'name': self.display_name,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': self.id,
            'target': 'current'
        }