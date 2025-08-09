from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class RequirementAssignments(models.Model):
    _name = "requirement.assignments"
    _description = "Assignments"

    # code = fields.Text(string='Code', readonly = True )
   
    businessdomain_category_id = fields.Many2one('requirement.business.domain.categories', required=True, string="Business Domain Category" )
    business_domain_id = fields.Many2one('requirement.business.domains', required=True, string="Business Domain",
                                                  domain="[('businessdomain_category_id', '=', businessdomain_category_id)]")
    company_id = fields.Many2one(
        'res.company', 
        string="Company",
    )

    active = fields.Boolean(string="Active", default=True, copy=False)
   
    group_id = fields.Many2one(
        'res.groups',
        string='Group',
        domain=lambda self: [('category_id', '=', self.env.ref('requirement.module_category_bra').id)]
    )
    user_id = fields.Many2one(
        'res.users', 
        string='Responsible User', domain="[('groups_id', 'in', [group_id])]"
    )
    company_domain = fields.Char(compute="_compute_company_domain", store=False)  # Non-stored, only for domain
   

    # @api.onchange('group_id')
    # def _onchange_group_id(self):
    #     if self.group_id:
    #         return {'domain': {'user_id': [('groups_id', 'in', [self.group_id.id])]}}
    #     else:
    #         return {'domain': {'user_id': []}}

    @api.depends('user_id')
    def _compute_company_domain(self):
        for record in self:
            if record.user_id:
                # Get the companies linked to the selected user_id
                company_ids = record.user_id.company_ids.ids
                record.company_domain = "[('id', 'in', %s)]" % company_ids
            else:
                # No companies available if no user is selected
                record.company_domain = "[]"