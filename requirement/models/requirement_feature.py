from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class RequirementFeature(models.Model):
    _name = "requirement.feature"
    _description = "Feature"

    code = fields.Text(string='Feature Code', readonly = True )
    name = fields.Text(string='Title', required=True,  )
    specifications = fields.Html(string='Specifications', required=True,  )

    # businessdomain_category_id = fields.Many2one('business.domain.categories', required=True, string="Business Domain Category", domain="[('active', '=', True)]")
    # business_domain_id = fields.Many2one('business.domains', required=True, string="Business Domain",
    #                                               domain="[('businessdomain_category_id', '=', businessdomain_category_id),('active', '=', True)]")
    feature_cat_id = fields.Many2one(comodel_name='requirement.feature.category', string='Feature Category', required=True,
                                       domain="[('active', '=', True)]")
    
    businessdomain_category_id =  fields.Many2one(string='Business Domain Category',
                                      related="feature_cat_id.business_domain_id.businessdomain_category_id", related_sudo=True, store=True,readonly = True)
    business_domain_id =  fields.Many2one(string='Business Domain',
                                      related="feature_cat_id.business_domain_id", related_sudo=True, store=True,readonly = True)
    tag_ids = fields.Many2many('requirement.tag', string='Tags',tracking=True)
    active = fields.Boolean(string="Active", default=True, copy=False)

    @api.constrains('name')
    def _check_unique_name(self):
        for record in self:
            if self.search_count([('id', '!=', record.id), ('name', '=', record.name),('feature_cat_id', '=', record.feature_cat_id.id)]) > 0:
                raise ValidationError("Name must be unique, per feature category!")

    @api.model_create_multi
    def create(self, vals_list):
        # Check if there is an open state in the second model
        for vals in vals_list:
            feature_cat_id = vals.get('feature_cat_id') 
            if feature_cat_id:
                feature_cat = self.env['requirement.feature.category'].browse(feature_cat_id)
                if 'code' not in vals:
                    seq_name = f'feature.seq.{feature_cat.name}.{feature_cat.id}'
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
                    vals['code'] = f'{feature_cat.code}{sequence.next_by_code(seq_name)}' 
        return  super(RequirementFeature, self).create(vals_list)