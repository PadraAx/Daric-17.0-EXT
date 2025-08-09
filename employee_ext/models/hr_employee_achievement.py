# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HrEmployeeAchievement(models.Model):
    _name = 'hr.employee.achievement'
    _description = 'Employee Achievement'

    date = fields.Date('Date')
    category = fields.Char('Category')
    description = fields.Char('Description')
    action = fields.Char('Action')
    employee_id = fields.Many2one('hr.employee', string="employee")
