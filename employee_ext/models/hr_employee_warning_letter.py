# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HrEmployeeWarningLetter(models.Model):
    _name = 'hr.employee.warning.letter'
    _description = 'Employee Warning Letters'

    issued_date = fields.Date(string="Issued Date")
    desc = fields.Char(string="Description")
    data = fields.Binary(string='File', help="Export file related to this Letter")
    filename = fields.Char('File Name')
    employee_id = fields.Many2one('hr.employee', string="employee")
