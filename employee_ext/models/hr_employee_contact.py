# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HrEmployeeContact(models.Model):
    _name = 'hr.employee.contact'
    _description = 'Employee Contact'   
    
    
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    job_id = fields.Many2one('hr.job', string='Job Position')
    contact_category = fields.Many2one('hr.employee.contact.category', string='Category', required=True)
    communication = fields.Char('communication', required=True)

 
    
class HrEmployeeContact(models.Model):
    _name = 'hr.employee.contact.category'
    _description = 'Employee Contact Category'
    
    
    name = fields.Char('name')