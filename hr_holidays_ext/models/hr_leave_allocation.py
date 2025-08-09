# -*- coding: utf-8 -*-
from datetime import datetime, date, time

from odoo import api, Command, fields, models, tools, _
from odoo.exceptions import UserError


class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    # @api.constrains('date_from', 'date_to', 'holiday_status_id')
    # def _check_date_range(self):
    #     for record in self:
    #         if record.employee_id:
    #             domain = [('id', '!=', record.id),
    #                       ('employee_id', '=', record.employee_id.id),
    #                       ('date_from', '<=', record.date_to),
    #                       ('date_to', '>=', record.date_from),
    #                       ('holiday_status_id', '=', record.holiday_status_id.id)]
    #             overlapping_records = self.search(domain)
    #             if overlapping_records:
    #                 emp_overlap_name = ','.join(overlapping_records.mapped('employee_id.name'))
    #                 raise UserError(f"Date range has overlap with another record with same type: {emp_overlap_name}")

    contract_id = fields.Many2one('hr.contract')
    number_of_days_display = fields.Float(
        'Duration (days)', compute=False, store=True,
        help="For an Accrual Allocation, this field contains the theorical amount of time given to the employee, due to a previous start date, on the first run of the plan. This can be manually edited.")
    number_of_hours_display = fields.Float(
        'Duration (hours)', compute=False, store=True,
        help="For an Accrual Allocation, this field contains the theorical amount of time given to the employee, due to a previous start date, on the first run of the plan. This can be manually edited.")

    @api.depends('number_of_days_display', 'number_of_hours_display')
    def _compute_number_of_hours_display(self):
        pass

    @api.depends('number_of_days')
    def _compute_number_of_days_display(self):
        pass

    def _prepare_holiday_values(self, employees):
        self.ensure_one()
        return [{
            'name': self.name,
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_status_id.id,
            'notes': self.notes,
            'number_of_days': self.number_of_days,
            'number_of_days_display': self.number_of_days_display,
            'number_of_hours_display': self.number_of_hours_display,
            'parent_id': self.id,
            'employee_id': employee.id,
            'employee_ids': [(6, 0, [employee.id])],
            'state': 'confirm',
            'allocation_type': self.allocation_type,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'accrual_plan_id': self.accrual_plan_id.id,
        } for employee in employees]
        
        
    @api.model_create_multi
    def create(self, vals_list):
        """ Override to avoid automatic logging of creation """
        for values in vals_list:
            if 'state' in values and values['state'] not in ('draft', 'confirm'):
                raise UserError(_('Incorrect state for new allocation'))
            employee_id = values.get('employee_id', False)
            if not values.get('department_id'):
                values.update({'department_id': self.env['hr.employee'].browse(employee_id).department_id.id})
        allocations = super(models.Model, self.with_context(mail_create_nosubscribe=True)).create(vals_list)
        allocations._add_lastcalls()
        for allocation in allocations:
            partners_to_subscribe = set()
            if allocation.employee_id.user_id:
                partners_to_subscribe.add(allocation.employee_id.user_id.partner_id.id)
            if allocation.validation_type == 'officer':
                partners_to_subscribe.add(allocation.employee_id.sudo().parent_id.user_id.partner_id.id)
                partners_to_subscribe.add(allocation.employee_id.leave_manager_id.partner_id.id)
            allocation.message_subscribe(partner_ids=tuple(partners_to_subscribe))
            if not self._context.get('import_file'):
                allocation.activity_update()
            if allocation.validation_type == 'no' and allocation.state == 'confirm':
                allocation.action_validate()
        return allocations
