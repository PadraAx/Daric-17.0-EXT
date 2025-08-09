from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class ERMRiskAssignment(models.Model):
    _name = "erm.risk.assignment"
    _description = "Risk Assignments"

    @api.depends('current_user_id','group_id')
    def _compute_allowed_categories(self):
        for rec in self:
            if rec.user_has_groups('erm.erm_group_admin'):
                mapped_assignments = self.env['erm.risk.category'].search([])
                if mapped_assignments:
                    rec.allowed_category_ids = mapped_assignments.mapped('id')
            else:
                if rec.current_user_id:
                    mapped_assignments = self.env['erm.risk.category'].search([('user_id', '=', rec.env.uid)])
                    if mapped_assignments:
                        rec.allowed_category_ids = mapped_assignments.mapped('id')
                else:
                    rec.allowed_category_ids = False

    active = fields.Boolean(string="Active", default=True, copy=False)
    current_user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    allowed_category_ids = fields.Many2many('erm.risk.category', compute='_compute_allowed_categories', string='Allowed Categories')
    category_id = fields.Many2one('erm.risk.category', 'Category', required=True, domain="[('id', 'in', allowed_category_ids)]")
    risk_source_id = fields.Many2one('erm.risk.source', 'Risk Source', domain="[('category_id', '=', category_id)]")
    affected_area_ids = fields.Many2many('erm.risk.affected.area', string='Affected Area', required=True, domain="[('category_id', '=', category_id)]")
   
    group_id = fields.Many2one(
        'res.groups',
        string='Group',
        domain=lambda self: [('category_id', '=', self.env.ref('erm.module_category_erm').id)])
    user_id = fields.Many2one('res.users', string='Responsible User', domain="[('groups_id', 'in', [group_id])]", required=True)

    