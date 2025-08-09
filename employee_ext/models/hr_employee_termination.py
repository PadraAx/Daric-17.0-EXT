# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HrEmployeeTermination(models.Model):
    _name = 'hr.employee.termination'
    _description = 'Employee Termination'


    reason = fields.Char(string="Reason", required=True)
    desc = fields.Char(string="Description")
    date = fields.Date(string="Date")
    termination_type = fields.Many2one('hr.termination.type', string="Termination Type")
    termination_status = fields.Selection([('voluntary', 'Voluntary'),
                                           ('involuntary', 'Involuntary')], string="Termination Status")
    employee_id = fields.Many2one('hr.employee', string="employee")
    clearance_form = fields.Binary(string='Clearance Form')
    filename = fields.Char('File Name')
