# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import itertools
import pytz
from datetime import timedelta, datetime
from collections import defaultdict

from odoo import api, fields, models, _
from odoo.addons.resource.models.utils import string_to_datetime, Intervals
from odoo.exceptions import ValidationError

from odoo.addons.hr_work_entry_contract_ext.tools.utility_tools import (
    get_employees_attendace,
    get_employees_shifts,
    get_public_hodilay,
    get_employees_leaves,
    get_absence_attendances,
    get_all_rules,
    garbage_cal_data_emp,
    get_shifts,
    get_holidays_shift,
    get_emp_total_attendance,
    get_emp_total_holiday,
    NightShift,
    set_shift_extended,
    limit_record_period,
    MISSION,
    ShiftMissionCalendar,
    get_hr_periods,
    get_has_mission,
    convert_tz_date
)


def get_day_info(shift, tz_offset, attendance):
    if shift:
        start = convert_tz_date(shift.start_datetime, 0, tz_offset)
        end = convert_tz_date(shift.end_datetime, 23.99, tz_offset)
    else:
        start = convert_tz_date(attendance.s_date, 0, tz_offset)
        end = convert_tz_date(attendance.e_date, 23.99, tz_offset)
    return start, end


def convert_utc_local(utc_obj, tz):
    return utc_obj.astimezone(pytz.timezone(tz))


class HrContract(models.Model):
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    work_entry_source = fields.Selection(selection_add=[('rule', 'By Rules - Planning'),
                                                        ('rule_att', 'By Rules - Attendances')],
                                         required=True,
                                         default='rule_att',
                                         ondelete={'rule': 'set default', 'rule_att': 'set default', },
                                         tracking=True,)

    @api.model
    def get_work_entry_data(self, rule, out, periods):
        local_date = out[0].astimezone(pytz.timezone(rule.resource_calendar_id.tz)).date()
        return {
            'name': "%s%s" % (rule.work_entry_type_id.name + ": " if rule.work_entry_type_id else "", self.employee_id.name),
            'date_start': out[0],
            'date_stop': out[1],
            'work_entry_type_id': rule.work_entry_type_id.id,
            'employee_id': self.employee_id.id,
            'company_id': self.company_id.id,
            'state': 'draft',
            'contract_id': self.id,
            'hr_period_id': periods.get(self.company_id.id, {}).get(str(local_date), False)
        }

    def fetch_data(self, start_dt, end_dt):
        return {
            'attendances': get_employees_attendace(self, start_dt, end_dt),
            'shifts': get_employees_shifts(self, start_dt, end_dt),
            'public_hodilays': get_public_hodilay(self, start_dt, end_dt),
            'leaves': get_employees_leaves(self, start_dt, end_dt),
            'absence_attendances': get_absence_attendances(self, start_dt, end_dt),
            'rules': get_all_rules(self),
            'hr_periods': get_hr_periods(self, start_dt, end_dt),
        }

    def get_emp_cal_data(self, cal_data, emp_id, resource):
        return {
            'emp_attendances': cal_data['attendances'].get(emp_id, []),
            'emp_shifts': cal_data['shifts'].get(emp_id, []) if cal_data['shifts'] else [],
            'public_hodilay': cal_data['public_hodilays'].get(resource.id, [])+cal_data['public_hodilays'].get(False, []),
            'emp_leaves': cal_data['leaves'].get(emp_id, []),
            'emp_absence_attendances': cal_data['absence_attendances'].get(emp_id, []),
            'resource_rules': cal_data['rules'].get(resource.id, []),
        }

    def get_night_shift(self, att):
        start_time = att.s_date
        start_min = start_time.hour * 60 + start_time.minute
        if start_min <= 150:
            night_start = (start_time + timedelta(days=-1)).replace(hour=18, minute=30, second=0)
        else:
            night_start = start_time.replace(hour=18, minute=30)
        night_end = (night_start + timedelta(days=1)).replace(hour=2, minute=30)
        return NightShift(night_start, night_end)

    @api.model
    def remove_work_entry(self, start_dt, end_dt):
        self.env['hr.work.entry'].sudo().search([('employee_id', 'in', self.employee_id.ids),
                                                 ('date_start', '>=', start_dt),
                                                 ('date_stop', '<=', end_dt),
                                                 ('active', 'in', (True, False)),
                                                 ('state', 'in', ('cancelled', 'conflict', 'validated', 'draft'))]).unlink()

    @api.model
    def calculate_rule(self, rules, localdict, periods):
        result = []
        for rule in rules:
            out = rule._compute_rule(localdict)
            if out and limit_record_period(out):
                result.append(self.get_work_entry_data(rule, out, periods))
        return result

    @api.model
    def _get_employee_data(self, cal_data):
        employee = self.employee_id
        resource = employee.resource_calendar_id
        emp_data = self.get_emp_cal_data(cal_data, employee.id, resource)
        return {
            'employee': employee,
            'resource': resource,
            'emp_data': emp_data,
            'rules': emp_data['resource_rules'],
            'total_attendance': get_emp_total_attendance(emp_data, resource.tz_offset),
            'total_holiday': get_emp_total_holiday(emp_data, resource.tz_offset),
        }

    def _check_validation(self, emp_dict):
        if any([not (rec.e_date and rec.s_date) for rec in emp_dict['total_attendance']]):
            raise ValidationError(_("Employee %s has incorrect attendance") % emp_dict['employee'].name)

    def _get_shift_related_mission(self, start, end, emp_dict, attendance, tz):
        local_start = convert_utc_local(start, tz).date()
        local_end = convert_utc_local(end, tz).date()
        local_att_s_date = convert_utc_local(attendance.s_date, tz).date()
        local_att_e_date = convert_utc_local(attendance.e_date, tz).date()
        start_shift, end_shift = max(local_start, local_att_s_date), min(local_end, local_att_e_date)
        delta = end_shift - start_shift
        return [
            ShiftMissionCalendar(
                emp_dict['resource'].min_start,
                emp_dict['resource'].max_start,
                start_shift+timedelta(days=i),
                emp_dict['employee'].id,
                emp_dict['resource'].tz_offset,
            ) for i in range(delta.days+1)
        ]

    def calculate_rule_contract(self, start_dt, end_dt):
        cal_data = self.fetch_data(start_dt, end_dt)
        self.remove_work_entry(start_dt, end_dt)
        periods = cal_data['hr_periods']
        work_entry_values = []
        for contract in self:
            if contract.employee_id.id == 400:
                a = 2
            contract_tz = contract.resource_calendar_id.tz
            emp_dict = contract._get_employee_data(cal_data)
            self._check_validation(emp_dict)
            total_len = len(emp_dict['total_attendance'])-1
            for index, attendance in enumerate(emp_dict['total_attendance']):
                shifts = get_shifts(emp_dict['emp_data']['emp_shifts'], attendance, contract_tz)
                if attendance.type == MISSION:
                    shifts = self._get_shift_related_mission(start_dt, end_dt, emp_dict, attendance, contract_tz)
                shifts_chain = itertools.chain(shifts)
                shift = True
                while shift:
                    try:
                        shift = next(shifts_chain)
                        shift = set_shift_extended(shift, emp_dict['total_attendance'])
                    except:
                        shift = False
                    if shift or not(len(shifts)):
                        day_start, day_end = get_day_info(shift, contract.resource_calendar_id.tz_offset, attendance)
                        localdict = {
                            'has_shift': bool(shift),
                            'is_holiday':  bool(get_holidays_shift(emp_dict['total_holiday'], shift)),
                            'has_mission': bool(get_has_mission(emp_dict['total_attendance'], attendance)),
                            'attendance': attendance,
                            'shift': shift,
                            'night_shift': contract.get_night_shift(attendance),
                            'timedelta': timedelta,
                            'datetime': datetime,
                            'next_att': emp_dict['total_attendance'][index+1] if index < total_len else False,
                            'previous_att': emp_dict['total_attendance'][index-1] if index else False,
                            'day_start': day_start,
                            'day_end': day_end,
                            'local_week_day': day_start.astimezone(pytz.timezone(contract_tz)).weekday()
                        }
                        work_entry_values.extend(contract.calculate_rule(emp_dict['rules'], localdict, periods))

            cal_data = garbage_cal_data_emp(cal_data, emp_dict['employee'].id)
        return work_entry_values

    def _get_contract_work_entries_values(self, date_start, date_stop):
        start_dt = pytz.utc.localize(date_start) if not date_start.tzinfo else date_start
        end_dt = pytz.utc.localize(date_stop) if not date_stop.tzinfo else date_stop
        contract_vals = []
        # FILTER Contracts
        other_source_contract = self.filtered(lambda obj: obj.work_entry_source not in ['rule', 'rule_att'])
        rule_source_contract = self - other_source_contract

        # RULE PROCESS
        if rule_source_contract and self._context.get('generate'):
            self.env['hr.work.entry'].search([('date_start', '>=', start_dt),
                                              ('date_stop', '<=', end_dt),
                                              ('contract_id', 'in', rule_source_contract.ids)]).unlink()
            work_entry_values = rule_source_contract.calculate_rule_contract(start_dt, end_dt)
            work_entry_values = list(filter(lambda item: item['date_start'] < item['date_stop'], work_entry_values))
            contract_vals += work_entry_values
        if other_source_contract:
            # other_source_vals = super(
            #     HrContract, other_source_contract)._get_contract_work_entries_values(date_start, date_stop)
            # contract_vals += other_source_vals
            ##############
            # By pass odoo work entry logic to avoid create extra work entry
            pass

        return contract_vals

    def _generate_work_entries(self, date_start, date_stop, force=False):
        # Generate work entries between 2 dates (datetime.datetime)
        # This method considers that the dates are correctly localized
        # based on the target timezone
        assert isinstance(date_start, datetime)
        assert isinstance(date_stop, datetime)
        self = self.with_context(tracking_disable=True)
        ##########
        # overwrite to by pass error
        ##########
        # canceled_contracts = self.filtered(lambda c: c.state == 'cancel')
        # if canceled_contracts:
        #     raise UserError(
        #         _("Sorry, generating work entries from cancelled contracts is not allowed.") + '\n%s' % (
        #             ', '.join(canceled_contracts.mapped('name'))))
        vals_list = []
        self.write({'last_generation_date': fields.Date.today()})

        intervals_to_generate = defaultdict(lambda: self.env['hr.contract'])
        # In case the date_generated_from == date_generated_to, move it to the date_start to
        # avoid trying to generate several months/years of history for old contracts for which
        # we've never generated the work entries.
        self.filtered(lambda c: c.date_generated_from == c.date_generated_to).write({
            'date_generated_from': date_start,
            'date_generated_to': date_start,
        })
        utc = pytz.timezone('UTC')
        for contract in self:
            contract_tz = (contract.resource_calendar_id or contract.employee_id.resource_calendar_id).tz
            tz = pytz.timezone(contract_tz) if contract_tz else pytz.utc
            contract_start = tz.localize(fields.Datetime.to_datetime(
                contract.date_start)).astimezone(utc).replace(tzinfo=None)
            contract_stop = datetime.combine(fields.Datetime.to_datetime(contract.date_end or datetime.max.date()),
                                             datetime.max.time())
            if contract.date_end:
                contract_stop = tz.localize(contract_stop).astimezone(utc).replace(tzinfo=None)
            if date_start > contract_stop or date_stop < contract_start:
                continue
            date_start_work_entries = max(date_start, contract_start)
            date_stop_work_entries = min(date_stop, contract_stop)
            if force:
                intervals_to_generate[(date_start_work_entries, date_stop_work_entries)] |= contract
                continue

            # For each contract, we found each interval we must generate
            # In some cases we do not want to set the generated dates beforehand, since attendance based work entries
            #  is more dynamic, we want to update the dates within the _get_work_entries_values function
            is_static_work_entries = contract.has_static_work_entries()
            last_generated_from = min(contract.date_generated_from, contract_stop)
            if last_generated_from > date_start_work_entries:
                if is_static_work_entries:
                    contract.date_generated_from = date_start_work_entries
                intervals_to_generate[(date_start_work_entries, last_generated_from)] |= contract

            last_generated_to = max(contract.date_generated_to, contract_start)
            if last_generated_to < date_stop_work_entries:
                if is_static_work_entries:
                    contract.date_generated_to = date_stop_work_entries
                intervals_to_generate[(last_generated_to, date_stop_work_entries)] |= contract

        for interval, contracts in intervals_to_generate.items():
            date_from, date_to = interval
            vals_list.extend(contracts._get_work_entries_values(date_from, date_to))

        if not vals_list:
            return self.env['hr.work.entry']

        return self.env['hr.work.entry'].create(vals_list)
