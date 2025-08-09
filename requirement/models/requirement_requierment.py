from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo import http
from odoo.http import request

class RequirementRequirement(models.Model):
    _name = "requirement.requirement"
    _description = "Requirement"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.depends('state','business_domain_id')
    def _compute_has_write_access(self):
        for rec in self:
            rec.has_write_access = False
            if not rec.id:
                rec.has_write_access = True
            elif rec.status != 'Cancelled':
                if rec.state in ['1']:
                    if rec.create_uid.id == self.env.uid:
                                rec.has_write_access = True
                                return
                elif rec.state in ['2']:
                    if rec.create_uid != self.env.uid:
                        group = self.env.ref('requirement.group_bra_reviewer')
                        group_id = group.id
                        assignement = self.env['requirement.assignments'].search_count([('business_domain_id', '=', rec.business_domain_id.id),
                                                                        ('user_id', '=', self.env.uid),
                                                                        ('group_id', '=', group_id),
                                                                        ('company_id', '=',  rec.company_id.id),
                                                                                                        ])
                        if assignement > 0:
                            review = self.env['requirement.review'].search_count([('create_uid', '=',self.env.uid),('parent_id', '=',rec.id)])
                            if review == 0:
                                rec.has_write_access = True
                                return
                elif rec.state in ['3']:
                    group = self.env.ref('requirement.group_bra_analyst')
                    group_id = group.id
                    assignement = self.env['requirement.assignments'].search_count([('business_domain_id', '=', rec.business_domain_id.id),
                                                                    ('user_id', '=', self.env.uid),
                                                                    ('group_id', '=', group_id),
                                                                    ('company_id', '=',  rec.company_id.id),
                                                                                                    ])
                    if assignement > 0:
                        rec.has_write_access = True
                        return
                elif rec.state in ['1']:
                    isCreator =  rec.create_uid.id == rec.env.uid
                    rec.has_write_access = isCreator
                    return  
                elif rec.state in ['5']: 
                    pass
      
    def _compute_is_manager(self):
        for rec in self:
            rec.is_manager = False
            if rec.user_has_groups('requirement.group_bra_admin'):
                rec.is_manager = True

    def _get_default_favorite_user_ids(self):
        return [(6, 0, [self.env.uid])]
    
    @api.model
    def _search_is_favorite(self, operator, value):
        if operator not in ['=', '!='] or not isinstance(value, bool):
            raise NotImplementedError(_('Operation not supported'))
        return [('favorite_user_ids', 'in' if (operator == '=') == value else 'not in', self.env.uid)]

    def _compute_is_favorite(self):
        print(self)
        for requirement in self:
            requirement.is_favorite = self.env.user in requirement.favorite_user_ids

    def _inverse_is_favorite(self):
        print(self)
        favorite_requirements = not_fav_requirements = self.env['requirement.requirement'].sudo()
        for requirement in self:
            if self.env.user in requirement.favorite_user_ids:
                favorite_requirements |= requirement
            else:
                not_fav_requirements |= requirement
                
        not_fav_requirements.write({'favorite_user_ids': [(4, self.env.uid)]})
        favorite_requirements.write({'favorite_user_ids': [(3, self.env.uid)]})

    requirement_type = fields.Selection(selection=[("1", "Business Requirement"), ("2", "Change Request"),],
        string='requirement Type' ,readonly = True, tracking=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)

    company_id = fields.Many2one('res.company', string="Company",required=True, domain="[('id', 'in', allowed_company_ids)]" )
    allowed_company_ids = fields.Many2many('res.company', compute='_compute_allowed_company', string='Allowed Companies')
    business_domain_id = fields.Many2one('requirement.business.domains', required=True, string="Business Domain",
                                                  domain="[('id', 'in', allowed_business_domain_ids)]")
    allowed_business_domain_ids = fields.Many2many('requirement.business.domains', compute='_compute_business_domains', string='Allowed Business Domain')
    businessdomain_category_id =  fields.Many2one(string='Business Domain Category',
                                      related="business_domain_id.businessdomain_category_id", related_sudo=True, store=True,readonly = True)
    req_code = fields.Char(string='Code', required=False, readonly = True, store =True, index=True, copy=True, tracking=False)
    name = fields.Char(string='Title' ,required=True, store =True, index=False, copy=True,  tracking=False)
    description = fields.Html(string='Description')
   
    state = fields.Selection(
        selection=[
            ("1", "Draft"),
            ("2", "In Review"),
            ("3", "In Anlysis"),
            ("4", "In Project"),
            ("5", "Implemented"),
        ],
        string='Stage', default="1",readonly=True , tracking=True)
    status = fields.Char(default="Draft", string='Status', readonly = True, tracking=True)
    critical_level_id = fields.Many2one('requirement.critical.level', string="Critical Level", readonly = True,)
    doc_ids_count = fields.Integer(string="Documents", compute="_compute_doc_ids_count")
    workspace_id = fields.Many2one('documents.folder', string="Workspace", readonly=True)
    parent_id = fields.Many2one('requirement.requirement', string='Parent Record')
    child_ids = fields.One2many('requirement.requirement', 'parent_id', string='Related Records')
    attachment_ids = fields.Many2many("ir.attachment", 
                                    relation="m2m_ir_requirement_attachments_rel", 
                                    column1="m2m1_id",
                                    column2="attachment1_id",domain=lambda self: [('res_model', '=', 'requirement')],
                                    string="Attachments")
    review_ids = fields.One2many('requirement.review', 
        'parent_id', 
        string='Reviews'
    )
    review_ids_count = fields.Integer(string="Reviews", compute="_compute_review_ids_count")
    reviews_point = fields.Float('Reviews Point', compute='_compute_reviews_point',
                                    group_operator='avg',   compute_sudo=True, store=True, readonly=True, digits=(10, 8))

    task_id = fields.Many2one(
        'project.task', 'Task', readonly=False)
    priority = fields.Selection([('0', 'Very Low'),
                                  ('1', 'Low'),
                                  ('2', 'Normal'),
                                  ('3', 'High')],
                                 string='Priority', default='0')
    has_write_access = fields.Boolean('Has write access', compute="_compute_has_write_access", default=True, readonly=True )
    tag_ids = fields.Many2many('requirement.tag', string='Tags',tracking=True)
    is_manager = fields.Boolean('Is manager', compute="_compute_is_manager",default=False, readonly=True)

    favorite_user_ids = fields.Many2many(
        'res.users', 'requirement_favorite_user_rel', 'requirement_id', 'user_id',
        default=_get_default_favorite_user_ids,
        string='Members')
    is_favorite = fields.Boolean(compute='_compute_is_favorite', inverse='_inverse_is_favorite', search='_search_is_favorite',
        compute_sudo=True, string='Favorite')
    active = fields.Boolean(string="Active", default=True, copy=False)

   
   
    
    def action_send_for_review(self):
        for rec in self:
            if rec.state == '1':
                rec.state = '2'
    def action_cancel(self):
        for rec in self:
            rec.status = 'Cancelled'

    def action_view_documents(self):
        """Action for smart button to view documents."""
        """Action to open related documents in the Documents app."""
        return {
            'name': 'Documents',
            'domain': [('folder_id', '=', self.workspace_id.id)],
            'view_mode': 'kanban,tree,form',
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'context': {'create': False},
        }
    
    def action_view_reviews(self):
        return {
            'name': 'Reviews',
            'domain': [('parent_id', '=', self.id)],
            'view_mode': 'tree,form',
            'res_model': 'requirement.review',
            'type': 'ir.actions.act_window',
            'context': {'create': True, 'delete': False},
        }
    
    def _check_same_value(self):
        # Ensure there are related records
        if not self.review_ids:
            return False  # No related records to check
        # Get the first related record's x_field value
        first_value = self.review_ids[0].critical_level_id.id
        # Check if all related records have the same x_field value
        for record in self.review_ids:
            if record.critical_level_id.id != first_value:
                return False
        # If the loop completes without returning False, all values are the same
        return True
    
    @api.depends('review_ids.critical_level_id')
    def _compute_reviews_point(self):
        for record in self:
            if record.review_ids:
                check_same = record._check_same_value()
                group = self.env.ref('requirement.group_bra_reviewer')
                group_id = group.id
                assignement_count = self.env['requirement.assignments'].search_count([('business_domain_id', '=', record.business_domain_id.id),
                                                                  ('group_id', '=', group_id),
                                                                  ('company_id', '=',  record.company_id.id),
                                                                  ])
                if len(record.review_ids) == assignement_count and check_same and self.review_ids[0].critical_level_id.active_to_next_state:
                        record.status = self.review_ids[0].critical_level_id.name
                        record.state = '3'
                elif check_same: 
                     record.status = self.review_ids[0].critical_level_id.name
                elif not check_same:
                    record.status = 'Disputed'

                
    def _compute_doc_ids_count(self):
        for record in self:
            record.doc_ids_count = self.env['documents.document'].search_count([('folder_id', '=', record.workspace_id.id)])

    def _compute_review_ids_count(self):
            self.review_ids_count = self.env['requirement.review'].search_count([('parent_id', '=', self.id)])

    @api.depends('user_id')
    def _compute_business_domains(self):
        for rec in self:
             if rec.user_id:
                mapped_assignments = self.env['requirement.assignments'].search([('user_id', '=', rec.env.uid)])
                rec.allowed_business_domain_ids = mapped_assignments.mapped('business_domain_id').ids
             else:
                 rec.allowed_business_domain_ids = False

    @api.depends('user_id')
    def _compute_allowed_company(self):
        for rec in self:
            if rec.user_id:
                mapped_assignments = self.env['requirement.assignments'].search([('user_id', '=', rec.env.uid)])
                rec.allowed_company_ids = mapped_assignments.mapped('company_id').ids
            else:
                 rec.allowed_company_ids = False
    
    @api.constrains('business_domain_id')
    def _check_requirement_type(self):
        for record in self:
            if (not (record.business_domain_id.module_state != "installed" or (record.business_domain_id.module_state == "installed" and record.business_domain_id.imp_status == "1"))):
               record.requirement_type ="2" 
            elif (record.business_domain_id.imp_status not in ['2','3']):
               record.requirement_type ="1"

    @api.model_create_multi
    def create(self, vals_list):
        # Check if there is an open state in the second model
        for vals in vals_list:
            business_domain_id = vals.get('business_domain_id') 
            if business_domain_id:
                business_domain = self.env['requirement.business.domains'].browse(business_domain_id)
                if 'req_code' not in vals:
                    seq_name = f'business_requirement.seq.{business_domain.name}.{ business_domain.id}'
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
                    vals['req_code'] = f'{ business_domain.code}-{sequence.next_by_code(seq_name)}'
                # if 'name' in vals:
                #     parent_folder = self.env['documents.folder'].search([('name', '=', 'requirements')], limit=1)
                #     if not parent_folder:
                #         parent_folder = self.env['documents.folder'].sudo().create({
                #                         'name': "requirements" ,
                #                         'parent_folder_id': False,  # Or set a specific parent folder if needed
                #                                 })
                #     folder = self.env['documents.folder'].sudo().create({
                #                         'name': vals.get('name') ,
                #                         'parent_folder_id': parent_folder.id,  # Or set a specific parent folder if needed
                #                                 })
                #     vals['workspace_id'] = folder.id
        return  super(RequirementRequirement, self).create(vals_list)
    
        # def _message_post_after_hook(self, message, msg_vals):
      
    #     m2m_commands = msg_vals['attachment_ids']
    #     attachments = self.env['ir.attachment'].browse([x[1] for x in m2m_commands])
    #     partner = self.env['res.partner'].find_or_create(msg_vals['email_from']).id
    #     documents = self.env['documents.document'].create([{
    #         'name': attachment.name,
    #         'attachment_id': attachment.id,
    #         'folder_id': self.workspace_id.id,
    #         'owner_id':  self.create_uid.id,
    #         'partner_id': partner,
            
    #     } for attachment in attachments])
    #     for (attachment, document) in zip(attachments, documents):
    #         attachment.write({
    #             'res_model': 'requierment',
    #             'res_id': self.id,
    #         })
    
    #     return super(Requierment, self)._message_post_after_hook(message, msg_vals)
    

