from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class RequirementRequierment(models.Model):
    _inherit = "requirement.review"

    @api.depends('critical_level_id')
    def _compute_point(self):
        for record in self:
            if record:
                if record.critical_level_id.critical_point:
                    clp = int(record.critical_level_id.critical_point)
                    group = self.env.ref('requirement.group_bra_reviewer')
                    group_id = group.id
                    assignement = self.env['requirement.assignments'].search([('business_domain_id', '=', record.parent_id.business_domain_id.id),
                                                                  ('user_id', '=', record.create_uid.id),
                                                                  ('group_id', '=', group_id),
                                                                  ('company_id', '=',  record.parent_id.company_id.id),
                                                                  ], limit=1)
                    wf = int(assignement.weight_factor)
                    record.point = wf * clp

    point = fields.Float('Point', compute='_compute_point',stored=True, digits=(10, 8))
    critical_point = fields.Selection(
            string='Critical Point', readonly=True , related="critical_level_id.critical_point", stored=True) 