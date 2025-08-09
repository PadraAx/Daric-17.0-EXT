from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo import http
from odoo.http import request

class RequirementRequirement(models.Model):
    _inherit = "requirement.requirement"
   
    reviews_point = fields.Float('Reviews Point', compute='_compute_reviews_point',
                                    group_operator='avg',   compute_sudo=True, store=True, readonly=True, digits=(10, 8))
    
    @api.depends('review_ids.critical_level_id')
    def _compute_reviews_point(self):
        for record in self:
            if record.review_ids:
                check_same = record._check_same_value()
                if  check_same :
                        record.status = self.review_ids[0].critical_level_id.name
                elif not check_same:
                    record.status = 'Disputed'

                total_sum = round(sum(rec.point for rec in record.review_ids),4)
                record.reviews_point = total_sum
                BD = self.env['requirement.business.domains'].sudo().search([('id', '=', record.business_domain_id.id)], limit=1)
                if BD.min_score <= total_sum and record.state == '2':
                        critical_level_records = self.env['requirement.critical.level'].search([("active_to_next_state", "=", True)])
                        if critical_level_records:
                            record.status = critical_level_records[0].name
                        record.state = '3'
