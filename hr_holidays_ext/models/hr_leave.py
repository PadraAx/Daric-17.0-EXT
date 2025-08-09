# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import pytz

from lxml import etree
from pytz import timezone, UTC
from math import ceil
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, time
from odoo.tools.misc import format_date
from odoo.addons.resource.models.utils import float_to_time, HOURS_PER_DAY


def convert_float_hour(float_number):
    float_number = float_number or 0
    hours = int(float_number)
    minutes = int((float_number - hours) * 60)
    return f"{hours}:{minutes:02d}"


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    # request_unit_hours = fields.Boolean(
    #     'Custom Hours', compute='_compute_request_unit_hours', store=True, readonly=True, default=True)
    # req_hour_from = fields.Float(string='From')
    # req_hour_to = fields.Float(string='To')
    request_hour_from = fields.Float(string='Hour from')
    request_hour_to = fields.Float(string='Hour to')
    status_leave_type = fields.Selection(related='holiday_status_id.leave_type', readonly=True)
    holiday_status_id = fields.Many2one("hr.leave.type", compute="_compute_from_employee_id", store=True, string="Time Off Type", required=True, readonly=False, tracking=True,
                                        domain="""[('leave_type','!=','mission'), ('company_id', 'in', [employee_company_id, False]),
                                    '|', ('requires_allocation', '=', 'no'), ('has_valid_allocation', '=', True),]""")
    employee_ids = fields.Many2many('hr.employee', compute='_compute_from_holiday_type', store=True, string='Employees', readonly=True, groups=None,
                                    domain=lambda self: self._get_employee_domain())
    approval_access = fields.Boolean(compute='_compute_access')
    company_country_id = fields.Many2one(string="Country", related='company_id.country_id', store=True)
    ref = fields.Integer(string='comet ref')

    @api.depends('user_id')
    def _compute_access(self):
        is_approver_group = self.env.user.has_group('hr_holidays.group_hr_holidays_responsible')
        is_holidays_user = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        for record in self:
            record.approval_access = False
            if self.env.user._is_admin():
                continue
            if record.state not in ('draft', 'confirm'):
                record.approval_access = True
            if record.status_leave_type == 'mission':
                record.approval_access = False
            if is_holidays_user and record.id:
                record.approval_access = True
            elif is_approver_group:
                if (record.employee_id.leave_manager_id.id == self.env.user.id
                        or record.employee_id.parent_id.id == self.env.user.employee_id.id):
                    record.approval_access = True

    @ api.depends('date_from', 'date_to', 'resource_calendar_id', 'holiday_status_id.request_unit')
    def _compute_duration(self):
        for holiday in self:
            days, hours = holiday._get_duration()
            holiday.number_of_hours = hours
            holiday.number_of_days = days

    def _get_duration(self, check_leave_type=True, resource_calendar=None):
        """
        This method is factored out into a separate method from
        _compute_duration so it can be hooked and called without necessarily
        modifying the fields and triggering more computes of fields that
        depend on number_of_hours or number_of_days.
        """
        self.ensure_one()
        resource_calendar = resource_calendar or self.resource_calendar_id
        if not self.date_from or not self.date_to or not resource_calendar:
            return (0, 0)
        hours, days = (0, 0)
        if self.holiday_status_id.dynamic_duration:
            days, hours = self._local_get_duration(resource_calendar)
        else:
            days, hours = self._super_get_duration(
                check_leave_type=check_leave_type, resource_calendar=resource_calendar)
        return (days, hours)

    def _local_get_duration(self, resource_calendar):
        # check hourly
        hour_p_day = resource_calendar.max_start - resource_calendar.min_start
        if self.request_unit_hours and not self.leave_type_request_unit == 'day':
            if self.request_hour_to < self.request_hour_from:
                hours = 0
            else:
                hours = self.request_hour_to - self.request_hour_from
            days = hours / hour_p_day
        # check daily
        else:
            days = (self.request_date_to - self.request_date_from).days + 1
            hours = days * hour_p_day
        return (days, hours)

    def _super_get_duration(self, check_leave_type=True, resource_calendar=None):
        check_leave_type = False if self.holiday_status_id.by_pass_leave else check_leave_type
        if self.employee_id:
            # We force the company in the domain as we are more than likely in a compute_sudo
            domain = [('time_type', '=', 'leave'),
                      ('company_id', 'in', self.env.companies.ids + self.env.context.get('allowed_company_ids', [])),
                      # When searching for resource leave intervals, we exclude the one that
                      # is related to the leave we're currently trying to compute for.
                      '|', ('holiday_id', '=', False), ('holiday_id', '!=', self.id)]
            if self.leave_type_request_unit == 'day' and check_leave_type:
                # list of tuples (day, hours)
                work_time_per_day_list = self.employee_id.with_context(
                    calc_weekends=self.holiday_status_id.calc_weekends,
                ).list_work_time_per_day(
                    self.date_from,
                    self.date_to,
                    calendar=resource_calendar,
                    domain=domain)
                days = len(work_time_per_day_list)
                hours = sum(map(lambda t: t[1], work_time_per_day_list))
            else:
                work_days_data = self.employee_id.with_context(
                    calc_weekends=self.holiday_status_id.calc_weekends
                )._get_work_days_data_batch(
                    self.date_from,
                    self.date_to,
                    compute_leaves=check_leave_type,
                    domain=domain,
                    calendar=resource_calendar)[self.employee_id.id]
                hours, days = work_days_data['hours'], work_days_data['days']
        else:
            today_hours = resource_calendar.get_work_hours_count(
                datetime.combine(self.date_from.date(), time.min),
                datetime.combine(self.date_from.date(), time.max),
                False)
            hours = resource_calendar.get_work_hours_count(self.date_from, self.date_to)
            days = hours / (today_hours or HOURS_PER_DAY)
        if self.leave_type_request_unit == 'day' and check_leave_type:
            days = ceil(days)
        return (days, hours)

    @api.constrains('date_from', 'date_to')
    def _check_validity(self):
        for leave in self:
            leave_type = leave.holiday_status_id
            if leave_type.requires_allocation == 'no':
                continue
            employees = leave._get_employees_from_holiday_type()
            date_from = leave.date_from.date()
            leave_data = leave_type.get_allocation_data(employees, date_from)
            max_excess = leave_type.max_allowed_negative if leave_type.allows_negative else 0
            for employee in employees:
                if leave_data[employee] and leave_data[employee][0] and leave_data[employee][0][1]:
                    if leave_data[employee][0][1]['virtual_remaining_leaves'] < max_excess:
                        raise ValidationError(_("%s don't have hour time off in %s type. Remaining time off in this type is %s.") % (
                            employee.name,
                            leave_type.name,
                            leave_data[employee][0][1]['virtual_remaining_leaves']
                        ))

    @api.constrains('request_date_from')
    def _check_period(self):
        for leave in self:
            periods = self.env['hr.payroll.period'].search([
                ('date_to', '>=', leave['request_date_from']),
                ('date_from', '<=', leave['request_date_from']),
                ('company_id', '=', leave.company_id.id),
            ])
            if periods.filtered(lambda item: item.status != 'open'):
                raise AccessError(_("You have access to create time off only in open payment period."))

    @api.depends('holiday_status_id', 'request_unit_half')
    def _compute_request_unit_hours(self):
        for holiday in self:
            if (holiday.holiday_status_id and not holiday.request_unit_hours) or holiday.request_unit_half:
                holiday.request_unit_hours = False

    def action_validate(self):
        current_employee = self.env.user.employee_id
        leaves = self._get_leaves_on_public_holiday()
        # if leaves:
        #     raise ValidationError(_('The following employees are not supposed to work during that period:\n %s') % ','.join(leaves.mapped('employee_id.name')))

        if any(holiday.state not in ['confirm', 'validate1'] and holiday.validation_type != 'no_validation' for holiday in self):
            raise UserError(_('Time off request must be confirmed in order to approve it.'))

        self.write({'state': 'validate'})

        leaves_second_approver = self.env['hr.leave']
        leaves_first_approver = self.env['hr.leave']

        for leave in self:
            if leave.validation_type == 'both':
                leaves_second_approver += leave
            else:
                leaves_first_approver += leave

            if leave.holiday_type != 'employee' or\
                    (leave.holiday_type == 'employee' and len(leave.employee_ids) > 1):
                employees = leave._get_employees_from_holiday_type()

                conflicting_leaves = self.env['hr.leave'].with_context(
                    tracking_disable=True,
                    mail_activity_automation_skip=True,
                    leave_fast_create=True
                ).search([
                    ('date_from', '<=', leave.date_to),
                    ('date_to', '>', leave.date_from),
                    ('state', 'not in', ['cancel', 'refuse']),
                    ('holiday_type', '=', 'employee'),
                    ('employee_id', 'in', employees.ids)])

                if conflicting_leaves:
                    employees = employees.filtered(lambda emp: emp not in conflicting_leaves.employee_id.ids)
                    # for emp in employees
                    # # YTI: More complex use cases could be managed in master
                    # if leave.leave_type_request_unit != 'day' or any(l.leave_type_request_unit == 'hour' for l in conflicting_leaves):
                    #     raise ValidationError(_('You can not have 2 time off that overlaps on the same day.'))

                    # conflicting_leaves._split_leaves(leave.request_date_from, leave.request_date_to + timedelta(days=1))

                values = leave._prepare_employees_holiday_values(employees)
                leaves = self.env['hr.leave'].with_context(
                    tracking_disable=True,
                    mail_activity_automation_skip=True,
                    leave_fast_create=True,
                    no_calendar_sync=True,
                    leave_skip_state_check=True,
                    # date_from and date_to are computed based on the employee tz
                    # If _compute_date_from_to is used instead, it will trigger _compute_number_of_days
                    # and create a conflict on the number of days calculation between the different leaves
                    leave_compute_date_from_to=True,
                ).create(values)

                leaves._validate_leave_request()
            if leave.holiday_type == 'employee' and len(leave.employee_ids.ids) == 1:
                employee_id = leave.employee_ids.ids[0]
                conflicting_leaves = self.env['hr.leave'].with_context(
                    tracking_disable=True,
                    mail_activity_automation_skip=True,
                    leave_fast_create=True
                ).search([
                    ('date_from', '<=', leave.date_to),
                    ('date_to', '>', leave.date_from),
                    ('state', 'not in', ['cancel', 'refuse']),
                    ('holiday_type', '=', 'employee'),
                    ('id', '!=', leave.id),
                    ('employee_id', '=', employee_id)])
                if conflicting_leaves:
                    if any(item.holiday_status_id.leave_type == leave.holiday_status_id.leave_type for item in conflicting_leaves):
                        raise ValidationError(_('You can not have 2 time off that overlaps on the same day.'))
                leave.employee_id = employee_id
                leave.state = 'validate'

        leaves_second_approver.write({'second_approver_id': current_employee.id})
        leaves_first_approver.write({'first_approver_id': current_employee.id})

        employee_requests = self.filtered(lambda hol: hol.holiday_type == 'employee')
        employee_requests._validate_leave_request()
        if not self.env.context.get('leave_fast_create'):
            employee_requests.filtered(lambda holiday: holiday.validation_type != 'no_validation').activity_update()
        return True

    @api.constrains('date_from', 'date_to', 'employee_id')
    def _check_date(self):
        if self.env.context.get('leave_skip_date_check', False):
            return

        all_employees = self.employee_id | self.employee_ids
        all_leaves = self.search([
            ('date_from', '<', max(self.mapped('date_to'))),
            ('date_to', '>', min(self.mapped('date_from'))),
            ('employee_id', 'in', all_employees.ids),
            ('id', 'not in', self.ids),
            ('state', 'not in', ['cancel', 'refuse']),
        ])
        for holiday in self:
            domain = [
                ('date_from', '<', holiday.date_to),
                ('date_to', '>', holiday.date_from),
                ('id', '!=', holiday.id),
                ('state', 'not in', ['cancel', 'refuse']),
            ]

            employee_ids = (holiday.employee_id | holiday.employee_ids).ids
            search_domain = domain + [('employee_id', 'in', employee_ids),
                                      ('holiday_status_id.leave_type', 'in', all_leaves.holiday_status_id.mapped('leave_type'))]
            conflicting_holidays = all_leaves.filtered_domain(search_domain)
            if conflicting_holidays and any(conflicting_holiday.holiday_status_id.leave_type == holiday.holiday_status_id.leave_type for conflicting_holiday in conflicting_holidays):
                conflicting_holidays_list = []
                # Do not display the name of the employee if the conflicting holidays have an employee_id.user_id equivalent to the user id
                holidays_only_have_uid = bool(holiday.employee_id)
                holiday_states = dict(conflicting_holidays.fields_get(allfields=['state'])['state']['selection'])
                for conflicting_holiday in conflicting_holidays:
                    conflicting_holiday_data = {}
                    conflicting_holiday_data['employee_name'] = conflicting_holiday.employee_id.name
                    conflicting_holiday_data['date_from'] = format_date(
                        self.env, min(conflicting_holiday.mapped('date_from')))
                    conflicting_holiday_data['date_to'] = format_date(
                        self.env, min(conflicting_holiday.mapped('date_to')))
                    conflicting_holiday_data['state'] = holiday_states[conflicting_holiday.state]
                    if conflicting_holiday.employee_id.user_id.id != self.env.uid:
                        holidays_only_have_uid = False
                    if conflicting_holiday_data not in conflicting_holidays_list:
                        conflicting_holidays_list.append(conflicting_holiday_data)
                if not conflicting_holidays_list:
                    return
                conflicting_holidays_strings = []
                if holidays_only_have_uid and not self.env.context.get('travel', True):
                    for conflicting_holiday_data in conflicting_holidays_list:
                        conflicting_holidays_string = _('from %(date_from)s to %(date_to)s - %(state)s',
                                                        date_from=conflicting_holiday_data['date_from'],
                                                        date_to=conflicting_holiday_data['date_to'],
                                                        state=conflicting_holiday_data['state'])
                        conflicting_holidays_strings.append(conflicting_holidays_string)
                    raise ValidationError(_("""\You've already booked time off which overlaps with this period:
                            %sAttempting to double-book your time off won't magically make your vacation 2x better!""", "\n".join(conflicting_holidays_strings)))
                for conflicting_holiday_data in conflicting_holidays_list:
                    conflicting_holidays_string = "\n" + _('%(employee_name)s - from %(date_from)s to %(date_to)s - %(state)s',
                                                           employee_name=conflicting_holiday_data['employee_name'],
                                                           date_from=conflicting_holiday_data['date_from'],
                                                           date_to=conflicting_holiday_data['date_to'],
                                                           state=conflicting_holiday_data['state'])
                    conflicting_holidays_strings.append(conflicting_holidays_string)
                if not self.env.context.get('travel'):
                    raise ValidationError(_(
                        "An employee already booked time off which overlaps with this period:%s",
                        "".join(conflicting_holidays_strings)))

    def _to_utc(self, date, hour, resource):
        if float(hour) >= 24.0:
            raise ValidationError(_("hour must be in 0..23"))
        hour = float_to_time(float(hour))
        holiday_tz = timezone(resource.tz or self.env.user.tz or 'UTC')
        return holiday_tz.localize(datetime.combine(date, hour)).astimezone(UTC).replace(tzinfo=None)

    @api.depends('number_of_hours_display')
    def _compute_number_of_hours_text(self):
        # YTI Note: All this because a readonly field takes all the width on edit mode...
        for leave in self:
            leave.number_of_hours_text = '%s%s %s%s' % (
                '' if leave.request_unit_half or leave.request_unit_hours else '(',
                convert_float_hour(leave.number_of_hours_display),
                _('Hours'),
                '' if leave.request_unit_half or leave.request_unit_hours else ')')

    def _prepare_employees_holiday_values(self, employees):
        self.ensure_one()
        return [{
            'name': self.name,
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_status_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'request_date_from': self.request_date_from,
            'request_date_to': self.request_date_to,
            'notes': self.notes,
            'number_of_days': 0,
            'parent_id': self.id,
            'employee_id': employee.id,
            'employee_ids': employee,
            'state': 'validate',
        } for employee in employees]

    def _check_approval_update(self, state):
        """ Check if target state is achievable. """
        if self.env.is_superuser():
            return

        current_employee = self.env.user.employee_id
        is_responsible = self.env.user.has_group('hr_holidays.group_hr_holidays_responsible')
        is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        is_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')

        for holiday in self:
            val_type = holiday.validation_type

            if not (is_manager or is_officer) and state != 'confirm':
                if state == 'draft':
                    if holiday.state == 'refuse':
                        raise UserError(_('Only a Time Off Manager can reset a refused leave.'))
                    if holiday.date_from and holiday.date_from.date() <= fields.Date.today():
                        raise UserError(_('Only a Time Off Manager can reset a started leave.'))
                    if holiday.employee_id != current_employee:
                        raise UserError(_('Only a Time Off Manager can reset other people leaves.'))
                else:
                    if val_type == 'no_validation' and current_employee == holiday.employee_id:
                        continue
                    # use ir.rule based first access check: department, members, ... (see security.xml)
                    holiday.check_access_rule('write')

                    # This handles states validate1 validate and refuse
                    if holiday.employee_id == current_employee\
                            and self.env.user != holiday.employee_id.leave_manager_id\
                            and not is_officer:
                        raise UserError(_('Only a Time Off Officer or Manager can approve/refuse its own requests.'))

                    if (state == 'validate1' and val_type == 'both') and holiday.holiday_type == 'employee':
                        if not (is_officer or is_responsible) and self.env.user != holiday.employee_id.leave_manager_id:
                            raise UserError(_('You must be either %s\'s manager or Time off Manager to approve this leave') % (
                                holiday.employee_id.name))

                    if (state == 'validate' and val_type == 'manager')\
                            and self.env.user != (holiday.employee_id | holiday.sudo().employee_ids).leave_manager_id\
                            and not is_officer:
                        if holiday.employee_id:
                            employees = holiday.employee_id
                        else:
                            employees = ', '.join(holiday.employee_ids.filtered(
                                lambda e: e.leave_manager_id != self.env.user).mapped('name'))
                        raise UserError(_('You must be %s\'s Manager to approve this leave', employees))

                    if not (is_officer or is_responsible) and (state == 'validate' and val_type == 'hr') and holiday.holiday_type == 'employee':
                        raise UserError(
                            _('You must either be a Time off Officer or Time off Manager to approve this leave'))

    @api.depends('state', 'employee_id', 'department_id')
    def _compute_can_approve(self):
        for holiday in self:
            try:
                if holiday.state == 'confirm' and holiday.validation_type == 'both':
                    holiday._check_approval_update('validate1')
                else:
                    holiday._check_approval_update('validate')
            except (AccessError, UserError):
                holiday.can_approve = False
            else:
                holiday.can_approve = True

    @api.ondelete(at_uninstall=False)
    def _unlink_if_correct_states(self):
        error_message = _('You cannot delete a time off which is in %s state')
        state_description_values = {elem[0]: elem[1] for elem in self._fields['state']._description_selection(self.env)}
        now = fields.Datetime.now()

        if not self.user_has_groups('hr_holidays.group_hr_holidays_user'):
            for hol in self:
                if hol.state not in ['draft', 'confirm', 'validate1']:
                    raise UserError(error_message % state_description_values.get(self[:1].state))
                if hol.sudo().employee_ids and not hol.employee_id:
                    raise UserError(_('You cannot delete a time off assigned to several employees'))
        else:
            for holiday in self.filtered(lambda holiday: holiday.state not in ['draft', 'cancel', 'confirm']):
                raise UserError(error_message % (state_description_values.get(holiday.state),))

    def action_approve(self, check_state=True):
        # if validation_type == 'both': this method is the first approval approval
        # if validation_type != 'both': this method calls action_validate() below

        # Do not check the state in case we are redirected from the dashboard
        if check_state and any(holiday.state != 'confirm' for holiday in self):
            raise UserError(_('Time off request must be confirmed ("To Approve") in order to approve it.'))

        for holiday in self:
            if holiday.employee_id.id == self.env.user.employee_id.id:
                raise UserError(_('Employees can not approve their own records.'))

        current_employee = self.env.user.employee_id
        self.filtered(lambda hol: hol.validation_type == 'both').write(
            {'state': 'validate1', 'first_approver_id': current_employee.id})

        # Post a second message, more verbose than the tracking message
        # comment this second email because we wanted to send just one email and we cant find code of first email yet

        # for holiday in self.filtered(lambda holiday: holiday.employee_id.user_id):
        #     user_tz = timezone(holiday.tz)
        #     utc_tz = pytz.utc.localize(holiday.date_from).astimezone(user_tz)
        #     # Do not notify the employee by mail, in case if the time off still needs Officer's approval
        #     notify_partner_ids = holiday.employee_id.user_id.partner_id.ids if holiday.validation_type != 'both' else []
        #     holiday.message_post(
        #         body=_(
        #             'Your %(leave_type)s planned on %(date)s has been accepted',
        #             leave_type=holiday.holiday_status_id.display_name,
        #             date=utc_tz.replace(tzinfo=None)
        #         ),
        #         partner_ids=notify_partner_ids)

        self.filtered(lambda hol: not hol.validation_type == 'both').action_validate()
        if not self.env.context.get('leave_fast_create'):
            self.activity_update()
        return True

    def action_refuse(self):
        current_employee = self.env.user.employee_id
        if any(holiday.state not in ['draft', 'confirm', 'validate', 'validate1'] for holiday in self):
            raise UserError(_('Time off request must be confirmed or validated in order to refuse it.'))

        for holiday in self:
            if holiday.employee_id.id == self.env.user.employee_id.id:
                raise UserError(_('Employees can not approve their own records.'))

        self._notify_manager()
        validated_holidays = self.filtered(lambda hol: hol.state == 'validate1')
        validated_holidays.write({'state': 'refuse', 'first_approver_id': current_employee.id})
        (self - validated_holidays).write({'state': 'refuse', 'second_approver_id': current_employee.id})
        # Delete the meeting
        self.mapped('meeting_id').write({'active': False})
        # If a category that created several holidays, cancel all related
        linked_requests = self.mapped('linked_request_ids')
        if linked_requests:
            linked_requests.action_refuse()

        # Post a second message, more verbose than the tracking message
        for holiday in self:
            if holiday.employee_id.user_id:
                holiday.message_post(
                    body=_('Your %(leave_type)s planned on %(date)s has been refused',
                           leave_type=holiday.holiday_status_id.display_name, date=holiday.date_from),
                    partner_ids=holiday.employee_id.user_id.partner_id.ids)

        self.activity_update()
        return True

    @api.model
    def create_from_rpc(self, values):
        self.with_context(leave_skip_state_check=True, hr_work_entry_no_check=True).create(values)
        return 1

# -----------------------------------
#   ORM METHODS
# -----------------------------------

    @api.model
    def get_views(self, views, options=None):
        read_only_fields = ['holiday_status_id', 'employee_ids', 'request_date_from',
                            'request_unit_hours', 'request_hour_from', 'request_hour_to',
                            'name', 'supported_attachment_ids', 'holiday_type']
        res = super().get_views(views, options)
        if res['views'].get('form'):
            data = etree.XML(res['views']['form']['arch'])
            for node in data.xpath('//field'):
                if node.get('name') in read_only_fields:
                    node.set('readonly', 'approval_access')
            res['views']['form']['arch'] = etree.tostring(data)
        return res

    def _notify_get_recipients_groups(self, message, model_description, msg_vals=None):
        """ Handle HR users and officers recipients that can validate or refuse holidays
        directly from email. """
        groups = super()._notify_get_recipients_groups(
            message, model_description, msg_vals=msg_vals
        )
        # OVERWRITE TO REMOVE USER GROUP
        if not self:
            return groups

        local_msg_vals = dict(msg_vals or {})

        self.ensure_one()
        hr_actions = []
        if self.state == 'confirm':
            app_action = self._notify_get_action_link('controller', controller='/leave/validate', **local_msg_vals)
            hr_actions += [{'url': app_action, 'title': _('Approve')}]
        if self.state in ['confirm', 'validate', 'validate1']:
            ref_action = self._notify_get_action_link('controller', controller='/leave/refuse', **local_msg_vals)
            hr_actions += [{'url': ref_action, 'title': _('Refuse')}]

        holiday_user_group_id = self.env.ref('hr_holidays.group_hr_holidays_responsible').id
        new_group = (
            'group_hr_holidays_responsible',
            lambda pdata: pdata['type'] == 'user' and holiday_user_group_id in pdata['groups'],
            {
                'actions': hr_actions,
                'active': True,
                'has_button_access': True,
            }
        )

        return [new_group] + groups

    def write(self, values):
        if 'active' in values and not self.env.context.get('from_cancel_wizard'):
            raise UserError(_("You can't manually archive/unarchive a time off."))

        is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user') or self.env.is_superuser()
        is_responsible = self.env.user.has_group('hr_holidays.group_hr_holidays_responsible')
        if not is_officer and not is_responsible and values.keys() - {'attachment_ids', 'supported_attachment_ids', 'message_main_attachment_id'}:
            if any(hol.date_from.date() < fields.Date.today() for hol in self):
                raise UserError(_('You must have manager rights to modify/validate a time off that already begun'))

        # Unlink existing resource.calendar.leaves for validated time off
        if 'state' in values and values['state'] != 'validate':
            validated_leaves = self.filtered(lambda l: l.state == 'validate')
            validated_leaves._remove_resource_leave()

        employee_id = values.get('employee_id', False)
        if not self.env.context.get('leave_fast_create'):
            if values.get('state'):
                self._check_approval_update(values['state'])
                if any(holiday.validation_type == 'both' for holiday in self):
                    if values.get('employee_id'):
                        employees = self.env['hr.employee'].browse(values.get('employee_id'))
                    else:
                        employees = self.mapped('employee_id')
                    self._check_double_validation_rules(employees, values['state'])
            if 'date_from' in values:
                values['request_date_from'] = values['date_from']
            if 'date_to' in values:
                values['request_date_to'] = values['date_to']
        result = super(models.Model, self).write(values)
        if not self.env.context.get('leave_fast_create'):
            for holiday in self:
                if employee_id:
                    holiday.add_follower(employee_id)

        return result
