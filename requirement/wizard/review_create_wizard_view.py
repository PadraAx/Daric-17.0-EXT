import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil import relativedelta
from datetime import date
from odoo.exceptions import UserError

class RequirementReviewCreateWizard(models.TransientModel):
    _name = "requirement.review.create.wizard"
    _description = "Requirement Review Create Wizard"
    
    # def _get_period_id(self):
    #     period_rec = self.env['performance.period'].sudo().search([('state', '=', 'in_progress')], limit=1)
    #     if period_rec:
    #         return period_rec.id
    #     else:
    #         raise UserError("Cannot create a record in Performance because there are no 'In Progress' states in Period.")
        
    @api.model
    def default_get(self, fields_list):
       active_id = self.env.context.get('active_id')
       res= super(RequirementReviewCreateWizard, self).default_get(fields_list)
       res['parent_id'] = active_id
       return res
    
    critical_level_id = fields.Many2one('requirement.critical.level', string="Critical Level", required=True)
    comments = fields.Html(string='Comments')
    parent_id = fields.Many2one('requirement.requirement', string='Related Requierment')
    tag_ids = fields.Many2many('requirement.tag', string='Tags',tracking=True)

   
    def action_reviewed(self):
        for record in self:
             performance = self.env['requirement.review'].create({
                'parent_id':  self.env.context.get('active_id') ,
                'critical_level_id': record.critical_level_id.id,
                'comments': record.comments,
            })  
        return {'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {'type': 'success',
                            'title': _("Successfully!"),
                            'message': _(f"Requirement has been reviewed."),
                            'next': {'type': 'ir.actions.act_window_close'},
                            }
                    }
    
  
