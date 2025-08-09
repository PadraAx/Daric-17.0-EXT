# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import date
from odoo import models, fields, api
from odoo.tools import SQL


class Users(models.Model):
    _inherit = 'res.users'

    def get_requierment_record(self):
        mapped_assignments = self.env['requirement.assignments'].search([('user_id', '=', self.env.uid)])
        domain_business_domain_id = mapped_assignments.mapped('business_domain_id').ids    
        domain_company =  mapped_assignments.mapped('company_id').ids  
        # domain_company = SQL(f'(select company_id from assignments where user_id = {self.env.user.id})')
        # domain_business_domain_id =  SQL(f'(select company_id from assignments where user_id = {self.env.user.id})')
        return [('state','in', ['2','3','4','5']),('company_id', 'in', domain_company),('business_domain_id', 'in', domain_business_domain_id)]
    
    def get_review_record_read(self):
        mapped_assignments = self.env['requirement.assignments'].search([('user_id', '=', self.env.uid)])
        domain_business_domain_id = mapped_assignments.mapped('business_domain_id').ids    
        domain_company =  mapped_assignments.mapped('company_id').ids  
        return [('parent_id.company_id', 'in', domain_company),('parent_id.business_domain_id', 'in', domain_business_domain_id)]
    
    def get_review_record_write(self):
        mapped_assignments = self.env['requirement.assignments'].search([('user_id', '=', self.env.uid)])
        domain_business_domain_id = mapped_assignments.mapped('business_domain_id').ids    
        domain_company =  mapped_assignments.mapped('company_id').ids  
        return [('create_uid', '=', self.env.uid),('parent_id.state', '=', '2'),('parent_id.company_id', 'in', domain_company),('parent_id.business_domain_id', 'in', domain_business_domain_id)]
