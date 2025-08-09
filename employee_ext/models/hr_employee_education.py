# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HrEmployeeDegree(models.Model):
    _name = 'hr.employee.degree'
    _description = 'Hr Degree'

    name = fields.Char('Name')

class HrEmployeeEducation(models.Model):
    _name = 'hr.employee.education'
    _description = 'Employee Education'


    degree = fields.Many2one('hr.employee.degree', string="Degree")
    university_name = fields.Char(string="University")
    specialisation_area_name = fields.Char(string="Specialisation Area")
    start = fields.Date(string="Start Date")
    finish = fields.Date(string="Finish Date")
    orientation = fields.Char('Orientation')
    employee_id = fields.Many2one('hr.employee', string="employee")
    certificate_file = fields.Binary(string='Certificate File', required=True)
    filename = fields.Char('File Name')
    res_user = fields.Many2one('res.users', string="User", related="employee_id.user_id", store=True)

    
    def _compute_display_name(self):
        for record in self:
            record.display_name = f'{record.employee_id.name}-{record.degree.name}'
