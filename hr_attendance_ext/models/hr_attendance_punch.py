# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError


class HrAttendancePunch(models.Model):
    _name = 'hr.attendance.punch'
    _description = 'Attendance Punch'
    _order = "date desc"
    

    @api.depends('employee_id', 'date')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.employee_id.name} | {str(record.date)}"


    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    date = fields.Datetime('Date Time', required=True)
