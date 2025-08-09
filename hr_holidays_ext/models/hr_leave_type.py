# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (c) 2005-2006 Axelor SARL. (http://www.axelor.com)

import logging
import pytz

from collections import defaultdict
from datetime import time, datetime

from odoo import api, fields, models
from odoo.tools import format_date
from odoo.tools.translate import _
from odoo.tools.float_utils import float_round
from odoo.addons.hr_work_entry_holidays.models.hr_leave import HrLeaveType

HrLeaveType.work_entry_type_id = fields.Many2one('hr.work.entry.type', string='Work Entry Type')
class HolidaysType(models.Model):
    _inherit = "hr.leave.type"


    leave_type = fields.Selection([('leave', 'Absence'),
                                   ('mission', 'Mission'),
                                   ('remote', 'Remote'), ], default=None, string="Leave Type",)
    hours_per_day = fields.Float(string='Hours per day(limit)', digits=(2, 4))
    day_per_month = fields.Integer(string='Days per Month(limit)',
                                   help="generate allocation while pay period update to open base one pay period")
    absence_type = fields.Selection([('PAID_HOURLY_TIME_OFF', 'Paid'),
                                    ('UNPAID_HOURLY_TIME_OFF', 'Unpaid'),
                                    ('SICK_TIME_OFF', 'Sick'),
                                    ('MATERNITY_TIME_OFF', 'Maternity'),
                                    ('PATERNITY_TIME_OFF', 'Paternity'),
                                    ('STUDY_TIME_OFF', 'Study'),
                                    ('FDR_DEATH_TIME_OFF', 'Compassionate'),
                                    ('MARRIAGE_TIME_OFF', 'Marriage'),
                                    ('DAILY_MISSION', 'Daily Mission'),
                                    ('HOURLY_MISSION', 'Hourly Mission'),
                                    ('PAID_SICK_TIME_OFF', 'Paid Sick'),
                                    ('UNPAID_SICK_TIME_OFF', 'UnPaid Sick'), 
                                    ('CASUAL_TIME_OFF', 'Casual Leave'),
                                    ('PARENTAL_TIME_OFF', 'Parental Leave'),
                                    ('CHILDCARE_TIME_OFF', 'Child Care Leave'),
                                    ('EXTENDED_CHILDCARE_TIME_OFF', 'Extended Child Care Leave'),
                                    ('SOLO_PARENTAL_TIME_OFF', 'Parental Leave For Solo Parent'),
                                    ('SPECIAL_FOR_WOMEN_TIME_OFF', 'Special Leave For Women'),
                                    ('VICTIM_OF_VIOLENCE_TIME_OFF', 'Victims of Violence'),
                                    ('R_SICK_TIME_OFF', 'R Sick')], string="Absence Type")
    by_pass_leave = fields.Boolean(string="Skipping Holidays", default=False,
                                   help="by pass leave during calculation of the duration on request")
    calc_weekends = fields.Boolean(string="Apply WeekEnds", default=False,
                                   help="calculate weekend resource attendace on the duration on request")
    dynamic_duration = fields.Boolean(string="Dynamic Duration", default=True,
                                      help="if its false we calculate duratoin base on resource calendar range")
    work_entry_type_id = fields.Many2one('hr.work.entry.type', string='Work Entry Type')


    @api.depends('requires_allocation', 'virtual_remaining_leaves', 'max_leaves', 'request_unit')
    @api.depends_context('holiday_status_display_name', 'employee_id', 'from_manager_leave_form')
    def _compute_display_name(self):
        ########################
        ########################
        # orver write to change display of the hourly time off
        if not self.requested_display_name():
            # leave counts is based on employee_id, would be inaccurate if not based on correct employee
            return super()._compute_display_name()
        for record in self:
            name = record.name
            if record.requires_allocation == "yes" and not self._context.get('from_manager_leave_form'):
                name = "{name} ({count})".format(
                    name=name,
                    count=_('%g remaining out of %g') % (
                        float_round(record.virtual_remaining_leaves, precision_digits=2) or 0.0,
                        float_round(record.max_leaves, precision_digits=2) or 0.0,
                    ) + (_(' days')),
                )
            record.display_name = name

    def get_allocation_data(self, employees, target_date=None):
        res = super(HolidaysType, self).get_allocation_data(employees, target_date)
        for emp, emp_data in res.items():
            resource_calendar = emp.resource_calendar_id
            calendar_duration = resource_calendar.max_start - resource_calendar.min_start
            for record in emp_data:
                data = record[1]
                if data['request_unit'] == 'hour':
                    max_leaves = data['max_leaves'] / calendar_duration
                    virtual_remaining_leaves = data['virtual_remaining_leaves'] / calendar_duration
                    data['max_leaves'] = float_round(max_leaves, precision_digits=2)
                    data['virtual_remaining_leaves'] = float_round(virtual_remaining_leaves, precision_digits=2)
        return res
