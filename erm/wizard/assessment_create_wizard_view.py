import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil import relativedelta
from datetime import date
from odoo.exceptions import UserError

class ERMRiskAssessmentCreateWizard(models.TransientModel):
    _name = "erm.risk.assessment.create.wizard"
    _description = "Risk Assessment Create Wizard"
    # def _get_period_id(self):
    #     period_rec = self.env['performance.period'].sudo().search([('state', '=', 'in_progress')], limit=1)
    #     if period_rec:
    #         return period_rec.id
    #     else:
    #         raise UserError("Cannot create a record in Performance because there are no 'In Progress' states in Period.")
        
    @api.model
    def default_get(self, fields_list):
       active_id = self.env.context.get('active_id')
       parent_id = self.env['erm.risk'].browse(active_id)
       res= super(ERMRiskAssessmentCreateWizard, self).default_get(fields_list)
       res['parent_id'] = active_id
    #    res['category_id'] = parent_id.category_id.id
       return res
    

    comments = fields.Html(string='Comments')
    parent_id = fields.Many2one(
        'erm.risk', 
        string='Related Risk'
    )
    tag_ids = fields.Many2many('erm.risk.tag', string='Tags',tracking=True)
    # category_id = fields.Many2one('erm.risk.category', 'Category',required=True)
    # category_type_id =  fields.Many2one(string='Category Type',
    #                                   related="category_id.category_type_id",  store=True,readonly = True)
    impact_id = fields.Many2one('erm.risk.impact', 'Impact',required=True)
    likelihood_id = fields.Many2one('erm.risk.likelihood', 'Likelihood',required=True) 
    
   
    def action_assessed(self):
        for record in self:
             assessment = self.env['erm.risk.assessment'].create({
                'parent_id':  self.env.context.get('active_id') ,
                # 'category_type_id': record.category_type_id.id,
                # 'category_id': record.category_id.id,
                'impact_id': record.impact_id.id,
                'likelihood_id': record.likelihood_id.id,
                'tag_ids': record.tag_ids.ids,
                'comments': record.comments,
            })
               
        return {'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {'type': 'success',
                            'title': _("Successfully!"),
                            'message': _(f"Risk has been assessed."),
                            'next': {'type': 'ir.actions.act_window_close'},
                            }
                    }
    
  
