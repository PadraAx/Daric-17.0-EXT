# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import pytz
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, exceptions, _
from odoo.tools import float_round


class HrEmployee(models.Model):
    _inherit = "hr.employee"


    last_attendance_id = fields.Many2one('hr.attendance', compute='_compute_last_attendance_id', store=True,
                            groups="hr_attendance.group_hr_attendance_officer,base.group_user")
    attendance_manager_id = fields.Many2one('res.users', store=True, readonly=False, domain="[('share', '=', False), ('company_ids', 'in', company_id)]", groups=None, tracking=True,
                help="The user set in Attendance will access the attendance of the employee through the dedicated app and will be able to edit them.")
    last_validated_timesheet_date = fields.Date(copy=False)


    def write(self, values):
        attendance_manager_id = False
        if 'attendance_manager_id' in values and values['attendance_manager_id']:
            attendance_manager_id = values.pop('attendance_manager_id')
            res = super(HrEmployee, self).write(values)
            super(models.Model, self).write({'attendance_manager_id':attendance_manager_id})
        else:
            res = super(HrEmployee, self).write(values)
        return res