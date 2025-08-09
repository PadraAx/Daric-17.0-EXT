# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, date
from collections import defaultdict
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from dateutil.relativedelta import relativedelta


class HrAttendanceRegenerationWizard(models.TransientModel):
    _name = 'hr.attendance.regeneration.wizard'
    _description = 'Regenerate Employee Attendance'

    
    @api.depends('hr_period_id')
    def _compute_date(self):
        self.date_from = self.hr_period_id and self.hr_period_id.date_from or False
        self.date_to = self.hr_period_id and self.hr_period_id.date_to or False
        
            
    hr_period_id = fields.Many2one("hr.payroll.period", string="Period", required=True, domain="[('status', '=', 'open')]")
    date_from = fields.Date('From', required=True, store=True, compute='_compute_date', precompute=True)
    date_to = fields.Date('To', required=True, store=True, compute='_compute_date', precompute=True)
    employee_ids = fields.Many2many('hr.employee', string='Employees', required=True)


    def regenerate_attendance_entries(self):
        self.calculate_attendance(self.employee_ids, self.date_from, self.date_to)
        return True

# ---------------------------------------------------
#  PROCESS LOGIC
# ---------------------------------------------------

    def fetch_dict_data(self, domain, model, field, order, employee_ids):
        if employee_ids:
            domain.append(('employee_id', 'in', employee_ids))
        out = defaultdict(list)
        data = self.env[model].sudo().search(domain, order=order)
        [out[getattr(item, field).id].append(item) for item in data]
        return out

    def get_employees_shifts(self, start_dt, end_dt, employee_ids):
        domain = [
            ('state', '=', 'published'),
            ('start_datetime', '<=', end_dt),
            ('end_datetime', '>=', start_dt),
        ]
        return self.fetch_dict_data(domain, 'planning.slot', 'employee_id', 'start_datetime ASC', employee_ids)

    def get_employees_punch(self, start_dt, end_dt, employee_ids):
        domain = [
            ('date', '<=', end_dt),
            ('date', '>=', start_dt),
        ]
        return self.fetch_dict_data(domain, 'hr.attendance.punch', 'employee_id', 'date ASC', employee_ids)

    def remove_attendance(self, start_dt, end_dt, employee_ids):
        domain = [
            ('check_in', '<=', end_dt),
            ('check_in', '>=', start_dt),
            ('att_type', '=', 'system')
        ]
        if employee_ids:
            domain.append(('employee_id', 'in', employee_ids))
        self.env['hr.attendance'].search(domain).unlink()

    def calculate_attendance(self, employee_ids, start, end):

        def make_attendance_record(emp_id, start, end):
            return {
                'employee_id': emp_id,
                'check_in': start,
                'check_out': end,
                'att_type': 'system',
            }

        def get_shift(punch, shifts):
            # TODO use btree algo to build left and right list
            if not shifts:
                return False
            right_shifts = list(filter(lambda item: item.start_datetime <= punch.date, shifts))
            left_shifts = list(filter(lambda item: item.end_datetime >= punch.date, shifts))
            if not right_shifts or not left_shifts:
                return (right_shifts and right_shifts[-1]) or (left_shifts and left_shifts[0])
            right_shift, left_shift = right_shifts[-1], left_shifts[0]
            right_dis = abs(right_shift.end_datetime - punch.date)
            left_dis = abs(left_shift.start_datetime - punch.date)
            return right_shift if right_dis < left_dis else left_shift

        def is_related(curr_punch, next_punch, shifts):
            curr_shift = get_shift(curr_punch, shifts)
            next_shift = get_shift(next_punch, shifts)
            if (curr_shift and next_shift
                    and curr_shift.start_datetime.date() != next_shift.start_datetime.date()
                    and not next_punch.date.date() < next_shift.start_datetime.date()
                    and next_shift != curr_shift):
                return False
            return True

        punches = self.get_employees_punch(start, end, employee_ids.ids)
        shifts = self.get_employees_shifts(start, end, employee_ids.ids)
        self.remove_attendance(start, end, employee_ids.ids)
        att_vals = []
        for emp_id, emp_punch in punches.items():
            # emp_punch.sort(key=lambda item: item.date)
            index, punch_len = 0, len(emp_punch)
            emp_shifts = shifts.get(emp_id)
            while index < punch_len:
                curr_punch = emp_punch[index]
                start = curr_punch.date
                next_punch = emp_punch[index+1] if index+1 < punch_len else False
                if next_punch and is_related(curr_punch, next_punch, emp_shifts):
                    end = next_punch.date
                    index += 2
                else:
                    end = False
                    index += 1
                att_vals.append(make_attendance_record(emp_id, start, end))
        self.env['hr.attendance'].create(att_vals)
