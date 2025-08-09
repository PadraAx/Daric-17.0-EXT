# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HrEmployeeDependent(models.Model):
    _name = 'hr.employee.dependent'
    _description = 'Employee Dependent'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Dependent Name", required=True, tracking=True)
    dob = fields.Date('Date of Birth', tracking=True)
    gender = fields.Selection([('male', 'Male'),
                                ('female', 'Female'),
                                ('other', 'Other')], tracking=True)
    relationship = fields.Many2one('hr.relationship.type', string="Relationship Type")
    emergency = fields.Boolean('Emergency')
    emergency_contact = fields.Char("Contact Name", tracking=True)
    emergency_phone = fields.Char("Contact Phone", tracking=True)
    visa_no = fields.Char('Visa No',  tracking=True)
    visa_expire = fields.Date('Visa Expire Date', tracking=True)
    emirates_no = fields.Char('Emirates No',  tracking=True)
    emirates_expire = fields.Date('Emirates No Expire Date', tracking=True)
    passport_id = fields.Char('Passport No',  tracking=True)
    passport_expire = fields.Date('Passport Expire Date', tracking=True)
    employee_id = fields.Many2one('hr.employee', string="employee")
