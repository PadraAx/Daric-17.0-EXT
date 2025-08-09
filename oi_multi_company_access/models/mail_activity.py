'''
Created on Aug 30, 2022

@author: Eman Khalifa
'''
from odoo import models

class MailActivity(models.Model):
    _inherit = 'mail.activity'
    
    def _check_access_assignation(self):
        for activity in self:
            user_company_id = False
            if activity.res_model and activity.sudo().user_id.company_group_ids:
                record = self.env[activity.res_model].sudo().browse(activity.res_id)
                user_company_id = activity.user_id.company_id
                if 'company_id' in record and record.company_id != user_company_id:
                    activity.user_id.company_id = record.company_id
                                
            super(MailActivity, activity)._check_access_assignation()
            
            if user_company_id:
                activity.user_id.company_id = user_company_id