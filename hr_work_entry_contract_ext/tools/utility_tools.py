# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from collections import defaultdict
from datetime import timedelta, date, datetime, timezone
from copy import deepcopy
import pytz

START_FIELDS = ['start_datetime', 'date_from', 'check_in']
END_FIELDS = ['end_datetime', 'date_to', 'check_out']

ATTENDANCE = 1
ABSENCE = 2
LEAVE = 3
MISSION = 4

LIMIT_RECORD = 60

LEAVE_TYPE = {
    'leave': LEAVE,
    'mission': MISSION,
    'remote': ATTENDANCE,
}


class DictToObject:
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                setattr(self, key, DictToObject(value))
            else:
                setattr(self, key, value)


def get_leave_type(leave):
    if leave.leave_type == 'mission' and leave.request_unit == 'HOURLY_MISSION':
        return ATTENDANCE
    return LEAVE_TYPE[leave.leave_type]


def convert_tz_date(att_date, hour, tz_offset):
    att_date_obj = att_date
    if isinstance(att_date, datetime):
        att_date_obj = att_date.date()
    date_obj = datetime.fromisoformat(str(datetime.strptime(
        f"{str(att_date_obj)} {str(timedelta(hours=hour))}{tz_offset}", "%Y-%m-%d %H:%M:%S%z")))
    return date_obj.astimezone(pytz.timezone('utc')).replace(tzinfo=None)


class NightShift(object):
    def __init__(self, start, end) -> None:
        self.s_date = start
        self.e_date = end


class Attendance(object):
    def __init__(self, obj, att_type, kind=False, sub_type=False, tz_offset=None) -> None:
        if isinstance(obj, dict):
            obj = type('new_dict', (object,), obj)
        s_attr = [getattr(obj, field) for field in START_FIELDS if hasattr(obj, field)]
        e_attr = [getattr(obj, field) for field in END_FIELDS if hasattr(obj, field)]
        self.s_date = s_attr[0] if s_attr else False
        self.e_date = e_attr[0] if e_attr else False
        self.type = att_type
        self.kind = kind
        self.sub_type = sub_type


class PublicHoliday(object):
    def __init__(self, obj, tz_offset=None) -> None:
        self.s_date = obj.date_from
        self.e_date = obj.date_to


class Shift(object):
    # this class used for extend the start and end of the shift
    # we do not want to edit the real shift
    def __init__(self, obj) -> None:
        self.start_datetime = obj.start_datetime
        self.end_datetime = obj.end_datetime
        self.extend = obj.extend
        self.employee_id = obj.employee_id.id


class ShiftMissionCalendar(object):
    # this class used for extend the start and end of the shift
    # we do not want to edit the real shift
    def __init__(self, hour_from, hour_to, att_date, employee_id, tz_offset) -> None:
        self.start_datetime = convert_tz_date(att_date, hour_from, tz_offset)
        self.end_datetime = convert_tz_date(att_date, hour_to, tz_offset)
        self.extend = 0
        self.employee_id = employee_id


class ShiftResourceCalendar(object):
    # this class used for extend the start and end of the shift
    # we do not want to edit the real shift
    def __init__(self, obj, att_date, employee_id, tz_offset) -> None:
        if len(obj) > 1:
            obj = obj[0]
        self.start_datetime = convert_tz_date(att_date, obj.hour_from, tz_offset)
        self.end_datetime = convert_tz_date(att_date, obj.hour_to, tz_offset)
        self.extend = 0
        self.employee_id = employee_id


def fetch_dict_data(self, domain, model, field, order):
    out = defaultdict(list)
    data = self.env[model].sudo().search(domain, order=order)
    [out[getattr(item, field).id].append(item) for item in data]
    return out


def get_employees_attendace(self, start_dt, end_dt):
    domain = [
        ('employee_id', 'in', self.employee_id.ids),
        ('check_in', '<=', end_dt),
        ('check_out', '>=', start_dt),
    ]
    return fetch_dict_data(self, domain, 'hr.attendance', 'employee_id', 'check_in ASC')


def get_employees_shifts(self, start_dt, end_dt):
    res = defaultdict(list)
    rule_work_entry = self.filtered(lambda contract: contract.work_entry_source == 'rule')
    rule_att_work_entry = self.filtered(lambda contract: contract.work_entry_source == 'rule_att')
    if rule_work_entry:
        domain = [
            ('employee_id', 'in', rule_work_entry.employee_id.ids),
            ('state', '=', 'published'),
            ('start_datetime', '<=', end_dt),
            ('end_datetime', '>=', start_dt),
        ]
        data = fetch_dict_data(self, domain, 'planning.slot', 'employee_id', 'start_datetime ASC')
        [res.update({emp: [Shift(shift) for shift in shifts]}) for emp, shifts in data.items()]
    if rule_att_work_entry:
        for contract in rule_att_work_entry:
            emp_id = contract.employee_id.id
            delta = end_dt - start_dt
            for i in range(delta.days+2):
                att = contract.resource_calendar_id.attendance_ids.filtered(lambda rec: rec.day_period != 'lunch')
                tz_offset = contract.resource_calendar_id.tz_offset
                att_date = start_dt+timedelta(days=i)
                res[emp_id].append(
                    ShiftResourceCalendar(
                        att.filtered(lambda x: int(x.dayofweek) == att_date.weekday()),
                        att_date,
                        emp_id,
                        tz_offset)
                )
        return res


def get_public_hodilay(self, start_dt, end_dt):
    domain = [
        '|', ('resource_id', 'in', self.employee_id.resource_id.ids), ('resource_id', '=', False),
        ('date_from', '<=', end_dt),
        ('date_to', '>=', start_dt),
        # these domain use to filter extra items come from holiday
        ('resource_id', '=', False),
        ('holiday_id', '=', False),
    ]
    return fetch_dict_data(self, domain, 'resource.calendar.leaves', 'calendar_id', 'date_from ASC')


def get_employees_leaves(self, start_dt, end_dt):
    domain = [
        ('employee_id', 'in', self.employee_id.ids),
        ('date_from', '<=', end_dt),
        ('date_to', '>=', start_dt),
        ('state', '=', 'validate'),
        ('holiday_status_id.leave_type', '!=', 'remote'),
    ]
    return fetch_dict_data(self, domain, 'hr.leave', 'employee_id', 'date_to ASC')


def get_hr_periods(self, start_dt, end_dt):
    domain = [
        ('date_from', '<=', end_dt),
        ('date_to', '>=', start_dt),
    ]
    periods = self.env['hr.payroll.period'].sudo().search(domain)
    # Initialize the dictionary with defaultdict
    data = defaultdict(lambda: defaultdict(list))
    # Process each period
    for period in periods:
        company_id = period.company_id.id
        # Ensure the dates are within the specified range
        current_start = max(period.date_from, start_dt.date())
        current_end = min(period.date_to, end_dt.date())

        # Populate the dictionary with dates for each company
        current_date = current_start
        while current_date <= current_end:
            data[company_id][current_date.strftime('%Y-%m-%d')] = period.id
            current_date += timedelta(days=1)
    return data


def get_absence_attendances(self, start_dt, end_dt):
    out = defaultdict(list)
    self._cr.execute('''
     SELECT
            shift.id, shift.employee_id,
            shift.end_datetime, shift.start_datetime
        FROM planning_slot AS shift
        LEFT JOIN hr_attendance AS att ON
            att.employee_id = shift.employee_id
            AND att.check_in <= shift.end_datetime
            AND att.check_out >= shift.start_datetime
        LEFT JOIN hr_leave AS leave ON
            leave.employee_id = shift.employee_id
            AND leave.date_from <= shift.end_datetime
            AND leave.date_to >= shift.start_datetime
            AND leave.state = 'validate'
        WHERE shift.start_datetime <= %s
            AND shift.end_datetime >= %s
            AND att.id IS null
            AND leave.id IS null
            AND shift.employee_id in %s
    ''', (end_dt, start_dt, tuple(self.employee_id.ids)))
    [out[item['employee_id']].append(item) for item in self._cr.dictfetchall()]
    return out


def convert_utc_local(utc_obj, tz):
    return utc_obj.astimezone(pytz.timezone(tz))


def get_shifts(emp_shifts, attendance, tz):
    local_att_sdate = convert_utc_local(attendance.s_date, tz).date()
    local_att_edate = convert_utc_local(attendance.e_date, tz).date()
    res = []
    for rec in emp_shifts:
        local_rec_sdate = convert_utc_local(rec.start_datetime, tz).date()
        local_rec_edate = convert_utc_local(rec.end_datetime, tz).date()
        if local_rec_sdate <= local_att_edate and local_rec_edate >= local_att_sdate:
            res.append(rec)
    return res


# def get_holidays_attendace(emp_holidays, attendance):
#     return list(filter(lambda item:
#                        (item.date_from <= attendance.s_date <= item.date_to) or
#                        (attendance.s_date <= item.date_from <= attendance.e_date),
#                        emp_holidays))


def get_holidays_shift(emp_holidays, shift):
    if not shift:
        return []
    return list(filter(lambda item:
                       (item.s_date <= shift.start_datetime <= item.e_date) or
                       (shift.start_datetime <= item.s_date <= shift.end_datetime),
                       emp_holidays))


def get_has_mission(total_attendance, attendance):
    mission_data = filter(lambda item: item.type == MISSION, total_attendance)
    return list(filter(lambda item:
                       (item.s_date <= attendance.s_date <= item.e_date) or
                       (attendance.s_date <= item.s_date <= attendance.e_date),
                       mission_data))


def get_emp_total_attendance(emp_data, tz_offset):
    emp_att = [Attendance(item, ATTENDANCE, tz_offset=tz_offset) for item in emp_data['emp_attendances']]
    emp_absence = [Attendance(item, ABSENCE, tz_offset=tz_offset) for item in emp_data['emp_absence_attendances']]
    emp_leaves = [Attendance(item,
                             get_leave_type(item.holiday_status_id),
                             item.holiday_status_id.request_unit,
                             item.holiday_status_id.absence_type,
                             tz_offset=tz_offset)
                  for item in emp_data['emp_leaves']]
    return sorted([*emp_att, *emp_absence, *emp_leaves], key=lambda item: item.s_date)


def get_emp_total_holiday(emp_data, tz_offset):
    emp_att = [PublicHoliday(item, tz_offset=tz_offset) for item in emp_data['public_hodilay']]
    return sorted(emp_att, key=lambda item: item.s_date)


def get_all_rules(self):
    # TODO  - add this from employee contract resource_calendar_id.rule_ids
    out = defaultdict(list)
    data = self.env['hr.attendance.rule'].search([])
    [out[item.resource_calendar_id.id].append(item) for item in data]
    return out


def get_first_attendance(shift, total_attendance):
    right_attendance = list(filter(lambda item: (item.type != 2
                                                 and item.s_date <= shift.end_datetime
                                                 and item.e_date >= shift.start_datetime), total_attendance))
    if not right_attendance:
        return False
    return sorted(right_attendance, key=lambda item: item.s_date)[0]


def set_shift_extended(shift, total_attendance):
    c_shift = deepcopy(shift)
    if c_shift.extend:
        first_attendance = get_first_attendance(c_shift, total_attendance)
        if first_attendance:
            diff = round((first_attendance.s_date - c_shift.start_datetime).total_seconds()/60)
            c_shift_extended = min(abs(diff), c_shift.extend) * (-1 if diff < 0 else 1)
            # update c_shift
            setattr(c_shift, 'start_datetime', c_shift.start_datetime + timedelta(minutes=c_shift_extended))
            setattr(c_shift, 'end_datetime', c_shift.end_datetime + timedelta(minutes=c_shift_extended))
    return c_shift


def limit_record_period(out):
    start_datetime = out[0]
    end_datetime = out[1]
    return (end_datetime-start_datetime).total_seconds() > LIMIT_RECORD


def garbage_cal_data_emp(cal_data, emp_id):
    cal_data['attendances'].pop(emp_id, None)
    cal_data['shifts'].pop(emp_id, None) if cal_data['shifts'] else None
    cal_data['leaves'].pop(emp_id, None)
    cal_data['absence_attendances'].pop(emp_id, None)
    return cal_data


'''
has_shift
and ( shift.start_datetime < attendance.s_date < shift.end_datetime
      or
      shift.start_datetime < attendance.e_date < shift.end_datetime)
and (not next_att or next_att.s_date < shift.end_datetime )

'''
