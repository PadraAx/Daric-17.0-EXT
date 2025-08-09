from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class RequirementRequierment(models.Model):
    _name = "requirement.review"
    _description = "Reviews"
    _rec_name = 'create_uid'

    @api.depends('parent_id.state')
    def _compute_has_write_access(self):
        for rec in self:
            rec.has_write_access = False
            if rec.create_uid.id == self.env.uid and rec.parent_id.state == '2':
                group = self.env.ref('requirement.group_bra_reviewer')
                group_id = group.id
                assignement = self.env['requirement.assignments'].search_count([('business_domain_id', '=', rec.parent_id.business_domain_id.id),
                                                                  ('user_id', '=', rec.create_uid.id),
                                                                  ('group_id', '=', group_id),
                                                                  ('company_id', '=',  rec.parent_id.company_id.id),
                                                                  ])
                if assignement> 0:
                    rec.has_write_access = True

    def _compute_is_manager(self):
        for rec in self:
            rec.is_manager = False
            if rec.user_has_groups('requirement.group_bra_admin'):
                rec.is_manager = True                  


 
    review_code =  fields.Text(string='Review Code')
    # partner_id = fields.Many2one(comodel_name='res.partner', string='Partner')
    # req_code = fields.Many2one('business.domains', string="Subdomain")
    critical_level_id = fields.Many2one('requirement.critical.level', string="Critical Level", required=True)
    comments = fields.Html(string='Comments')
    # doc_ids = fields.Many2many(comodel_name='documents.document', inverse_name='requierment_id',
    #                                    string='Documents')
  
    parent_id = fields.Many2one(
        'requirement.requirement', 
        string='Related Requierment'
    )
    tag_ids = fields.Many2many('requirement.tag', string='Tags',tracking=True)
    has_write_access = fields.Boolean('Has write access', compute="_compute_has_write_access", default=True, readonly=True )
    is_manager = fields.Boolean('Is manager', compute="_compute_is_manager",default=False, readonly=True)




    @api.model_create_multi
    def create(self, vals_list):
        # Check if there is an open state in the second model
        for vals in vals_list:
            parent_id = vals.get('parent_id') 
            if parent_id:
                parent_id = self.env['requirement.requirement'].browse(parent_id)
                if 'review_code' not in vals:
                    seq_name = f'business_requierment_review.seq.{parent_id.name}.{ parent_id.id}'
                    sequence = self.env['ir.sequence'].sudo().search([('code', '=', seq_name)], limit=1)
                    if not sequence:
                            sequence = self.env['ir.sequence'].sudo().create({
                                'name': seq_name,
                                'code': seq_name,
                                'padding': '2',  # Adjust padding as needed
                                'implementation': 'standard', 
                                'number_increment': '1', 
                                'number_next': '0', 
                            })
                    vals['review_code'] = f'{ parent_id.req_code}-{sequence.next_by_code(seq_name)}'
        return  super(RequirementRequierment, self).create(vals_list)
