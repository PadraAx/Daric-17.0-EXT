from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class RequirementBusinessDomains(models.Model):
    _name = "requirement.business.domains"
    _description = "Business Domains"

    code = fields.Char(string='Code', readonly = True)
    name = fields.Char(string='Title', required=True, readonly = False)
    # display_name = fields.Char(string='Display Name',required=False, readonly = True, store =False, index=False, copy=False,  tracking=False)
   
    businessdomain_category_id = fields.Many2one('requirement.business.domain.categories', required=True, string="Business Domain Category", domain="[('active', '=', True)]")
    module_id = fields.Many2one('ir.module.module', string="Module Technical Name")
    category_id =  fields.Many2one(string='Businessdomain Technical Category',
                                      related="businessdomain_category_id.category_id")
    module_state = fields.Selection(string='Module Status', related="module_id.state" , readonly=True)
    application = fields.Boolean("Application",  related="module_id.application" , readonly=True)
    icon_image = fields.Binary(string='Icon', related="module_id.icon_image" , readonly=True)

    active = fields.Boolean(string="Active", default=True, copy=False)
    imp_status = fields.Selection(
        selection=[
            ("1", "Not Implemented"),
            ("2", "Implementation in Progress"),
            ("3", "Implemented"),
        ],
        string='Implementation State',)
    project_ids = fields.Many2many("project.project", string="Projects", ondelete="restrict")
    description = fields.Html(string='Description')

    integration_ids = fields.One2many('requirement.business.domains.integration', 'parent_id', string="Integrations")

    _sql_constraints = [
        ('check_min_score', 'CHECK(min_score >= 0)', 'The Minimum score should be positive.'),
    ]

    @api.constrains('name','businessdomain_category_id')
    def _check_unique_name(self):
        for record in self:
            if self.search_count([('id', '!=', record.id), ('name', '=', record.name), ('businessdomain_category_id', '=', record.businessdomain_category_id.id)]) > 0:
                raise ValidationError("Name must be unique!")

    @api.model_create_multi
    def create(self, vals_list):
        # Check if there is an open state in the second model
        for vals in vals_list:
            category_id = vals.get('businessdomain_category_id') 
            if category_id:
                category = self.env['requirement.business.domain.categories'].browse(category_id)
                if 'code' not in vals:
                    seq_name =  f'business_domains.seq.{category.name}.{ category.id}'
                    sequence = self.env['ir.sequence'].search([('code', '=', seq_name)], limit=1)
                    if not sequence:
                            sequence = self.env['ir.sequence'].create({
                                'name': seq_name,
                                'code': seq_name,
                                'padding': '2',  # Adjust padding as needed
                                'implementation': 'standard', 
                                'number_increment': '1', 
                                'number_next': '0', 
                            })

                    vals['code'] =f'{category.code}{sequence.next_by_code(seq_name)}'
        return  super(RequirementBusinessDomains, self).create(vals_list)
    
