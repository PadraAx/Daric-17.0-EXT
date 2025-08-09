# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


def apply_notification(method):
    def inner(obj):
        method(obj)
        return {'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {'type': 'success' if obj.state in ("accept", "draft") else 'danger',
                           'title': _("Successfully!"),
                           'message': _(f"Status changed into {obj.state}"),
                           'next': {'type': 'ir.actions.act_window_close'},
                           }
                }
    inner.__wrapped__ = method
    return inner


class HrAttendanceMissing(models.Model):

    _name = 'hr.attendance.missing'
    _description = 'Missing Attendance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "create_date desc"

    @api.depends('employee_id', 'date')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.employee_id.name} | {str(record.date)}"

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    date = fields.Datetime('Date Time', required=True)
    state = fields.Selection([('draft', "Draft"),
                              ('accept', "Accept"),
                              ('reject', "Reject"),
                              ('cancel', "Cancel")], default='draft', required=True, string='State', tracking=True)
    punch_id = fields.Many2one('hr.attendance.punch', string="Punch", ondelete='set null', readonly=True)

# ---------------------------------------------------
#  Buttons
# ---------------------------------------------------
    @apply_notification
    def to_draft(self):
        self.write({'state': 'draft'})

    @apply_notification
    def to_accept(self):
        exit_punch = self.env['hr.attendance.punch'].search([
            ('employee_id', '=', self.employee_id.id),
            ('date', '=', self.date), ])
        if not exit_punch:
            res = self.env['hr.attendance.punch'].create({
                'employee_id': self.employee_id.id,
                'date': self.date
            })
            self.write({
                'punch_id': res.id,
                'state': 'accept',
            })
        else:
            raise UserError("Employee has punch with this date")

    @apply_notification
    def to_reject(self):
        if self.punch_id:
            raise UserError("Can not reject missing attendace while there is punch refrence")
        self.write({'state': 'reject'})

    @apply_notification
    def to_cancel(self):
        if self.punch_id:
            self.punch_id.unlink()
        self.write({'state': 'cancel'})
