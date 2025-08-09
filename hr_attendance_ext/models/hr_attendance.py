# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import pytz
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime
from odoo.exceptions import AccessError
from odoo.osv import expression
from datetime import timedelta, date, datetime, timezone


class HrAttendance(models.Model):
    _inherit = "hr.attendance"
    _order = "check_in desc"

    check_in = fields.Datetime(string="Check In", required=True, tracking=True, default=fields.Datetime.now)
    check_out = fields.Datetime(string="Check Out",  tracking=True)
    att_type = fields.Selection([('manual', 'Manual'),
                                 ('system', 'System'), ], default='manual', string="Attendance Type",)
    is_group_reader = fields.Boolean(compute='_compute_is_group_reader')
    hr_period_id = fields.Many2one("hr.payroll.period", compute="_compute_period",
                                   string="Period", readonly=True, required=True, store=True, precompute=True)

    @api.depends('employee_id')
    def _compute_is_group_reader(self):
        for record in self:
            record.is_group_reader = self.env.user.has_group('hr_attendance.group_hr_attendance_own_reader') and \
                not (self.env.user.has_group('hr_attendance.group_hr_attendance_officer')
                     or self.env.user.has_group('hr_attendance.group_hr_attendance_manager'))

    @api.depends('check_in', 'check_out', 'employee_id')
    def _compute_period(self):
        for attendance in self:
            periods = self.env['hr.payroll.period'].search([
                ('date_to', '>=', attendance['check_in']),
                ('date_from', '<=', attendance['check_out'] or attendance['check_in']),
                ('company_id', '=', attendance.employee_id.company_id.id)], order="date_from asc")
            attendance.hr_period_id = periods[0].id if len(periods) > 1 else periods.id

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee.
            For the same employee we must have :
                * maximum 1 "open" attendance record (without check_out)
                * no overlapping time slices with previous employee records
        """
        for attendance in self:
            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
            last_attendance_before_check_in = self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.id),
                ('check_in', '<=', attendance.check_in),
                ('id', '!=', attendance.id),
            ], order='check_in desc', limit=1)
            if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > attendance.check_in:
                raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s",
                                                   empl_name=attendance.employee_id.name,
                                                   datetime=format_datetime(self.env, attendance.check_in, dt_format=False)))

            if not attendance.check_out:
                # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
                no_check_out_attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_out', '=', False),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
                if no_check_out_attendances:
                    raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee hasn't checked out since %(datetime)s",
                                                       empl_name=attendance.employee_id.name,
                                                       datetime=format_datetime(self.env, no_check_out_attendances.check_in, dt_format=False)))
            if attendance.check_out:
                # we verify that the latest attendance with check_in time before our check_out time
                # is the same as the one before our check_in time computed before, otherwise it overlaps
                last_attendance_before_check_out = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_in', '<', attendance.check_out),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
                if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
                    raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s",
                                                       empl_name=attendance.employee_id.name,
                                                       datetime=format_datetime(self.env, last_attendance_before_check_out.check_in, dt_format=False)))

    @api.constrains('check_in', 'check_out')
    def _check_period(self):
        for attendance in self:
            periods = self.env['hr.payroll.period'].search(
                [('date_to', '>=', attendance['check_in']),
                 ('date_from', '<=', attendance['check_out']),
                 ('company_id', '=', attendance.employee_id.company_id.id)
                 ])
            if periods.filtered(lambda item: item.status != 'open'):
                raise AccessError(_("This payroll period has been closed. You cannot change related records."))

    def _default_hour(self, field, start):
        date_obj = date.today()
        if start:
            date_obj = datetime.strptime(start, '%Y-%m-%d %H:%M:%S').date()
        resource = self.env.user.employee_id.resource_calendar_id or self.env.user.company_id.resource_calendar_id
        time = getattr(resource, field)
        tz_offset = resource.tz_offset
        hour = datetime.fromisoformat(str(datetime.strptime(
            f"{str(date_obj)} {str(timedelta(hours=time))}{tz_offset}", "%Y-%m-%d %H:%M:%S%z")))
        return hour.astimezone(pytz.timezone('utc')).replace(tzinfo=None)

    @api.model
    def default_get(self, fields):
        res = super(HrAttendance, self).default_get(fields)
        if res.get('check_in'):
            start = self.env.context.get('check_out') or self.env.context.get('default_check_out')
            s_obj = res['check_in']
            e_obj = res.get('check_out', res['check_in'])
            if (e_obj - s_obj).days >= 1:
                start = False
            res['check_in'] = self._default_hour('min_start', start)
            res['check_out'] = self._default_hour('max_start', start)
        if res.get('check_in') and res['check_in'].date() == date.today():
            res['check_in'] = datetime.now()
            res['check_out'] = None
        return res

# -------------------------------------------------------------------------
# BUTTON
# -------------------------------------------------------------------------

    def action_new(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("hr_attendance.hr_attendance_action")
        return {'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {'type': 'success',
                           'title': _("Successfully!"),
                           'message': _(f"Attendance has been created."),
                           'next': action,
                           }
                }

    def action_delete(self):
        self.unlink()
        # action = self.env["ir.actions.act_window"]._for_xml_id("hr_attendance.hr_attendance_action")
        return {'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {'type': 'danger',
                           'title': _("Successfully!"),
                           'message': _(f"Attendance has been deleted."),
                           'next': {'type': 'ir.actions.act_window_close'},
                           }
                }

    # def action_save_new(self):
    #     view_id = self.env.ref('hr_attendance_ext.hr_attendance_ext_view_form').id
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': _('Create Attendance'),
    #         'view_mode': 'form',
    #         'res_model': 'hr.attendance',
    #         'target': 'new',
    #         'views': [(view_id, 'form')],
    #         'context': {
    #             'form_view_initial_mode': 'edit',
    #             'default_employee_id': self.employee_id.id,  # Example of pre-filling a field
    #         },
    #         'flags': {
    #             'form': {'action_buttons': True, 'options': {'mode': 'edit'}}
    #         }
    #     }

# -------------------------------------------------------------------------
# ORM
# -------------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res._update_overtime()
        return res

    def write(self, vals):
        if vals.get('employee_id') and \
                vals['employee_id'] not in self.env.user.employee_ids.ids and \
                not self.env.user.has_group('hr_attendance.group_hr_attendance_officer'):
            raise AccessError(_("Do not have access, user cannot edit the attendances that are not his own."))
        attendances_dates = self._get_attendances_dates()
        result = super(HrAttendance, self).write(vals)
        if any(field in vals for field in ['employee_id', 'check_in', 'check_out']):
            # Merge attendance dates before and after write to recompute the
            # overtime if the attendances have been moved to another day
            for emp, dates in self._get_attendances_dates().items():
                attendances_dates[emp] |= dates
            self._update_overtime(attendances_dates)
        return result

    def unlink(self):
        self._check_period()
        return super(HrAttendance, self).unlink()
