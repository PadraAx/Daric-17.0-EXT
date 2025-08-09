from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class RequirementBusinessDomainCategories(models.Model):
    _name = "requirement.business.domain.categories"
    _description = "Business Domain Categories"

    code = fields.Char(string='Code', required=False, readonly = True, index=True, copy=True)
    name = fields.Char(string='Title',required=True, readonly = False, store =True, index=False, copy=True,  tracking=False)
    # display_name = fields.Char(string='Display Name',required=False, readonly = False, store =False, index=False, copy=False,  tracking=False)
    category_id = fields.Many2one('ir.module.category', string='Technical Category', required=True, index=True, domain=[('parent_id','=', False), ('child_ids.module_ids', '!=', False)])
    active = fields.Boolean(string="Active", default=True, copy=False)

    @api.onchange('category_id')
    def _onchange_employee_id(self):
        for rec in self:
            category = rec.category_id.sudo()
            rec.name = category.name

    @api.constrains('name')
    def _check_unique_name(self):
        for record in self:
            if self.search_count([('id', '!=', record.id), ('name', '=', record.name)]) > 0:
                raise ValidationError("Name must be unique!")

    @api.model_create_multi
    def create(self, vals_list):
        # Check if there is an open state in the second model
        for vals in vals_list:
            # Check if 'code' is in vals, if not set a default value
            if 'code' not in vals:
                seq_name = 'business_domain_categories.seq'
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
                vals['code'] = sequence.next_by_code(seq_name)
        return  super(RequirementBusinessDomainCategories, self).create(vals_list)