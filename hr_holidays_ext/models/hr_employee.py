from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, datetime, time
from pytz import timezone


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'


    current_leave_id = fields.Many2one('hr.leave.type', compute='_compute_current_leave',
                                       string="Current Time Off Type", groups="base.group_user")
    leave_manager_id = fields.Many2one('res.users', string='Time Off',
                                        compute='_compute_leave_manager', store=True, readonly=False,
                                        domain="[('share', '=', False)]",
                                        tracking=True, )

    def _get_calendar_attendances(self, date_from, date_to):
        self.ensure_one()
        valid_contracts = self.sudo()._get_contracts(date_from, date_to, states=['open', 'close'])
        if not valid_contracts:
            return super()._get_calendar_attendances(date_from, date_to)
        employee_tz = timezone(self.tz) if self.tz else None
        duration_data = {'days': 0, 'hours': 0}
        for contract in valid_contracts:
            contract_start = datetime.combine(contract.date_start, time.min, employee_tz)
            contract_end = datetime.combine(contract.date_end or date.max, time.max, employee_tz)
            calendar = contract.resource_calendar_id or contract.company_id.resource_calendar_id
            contract_duration_data = calendar\
                .with_context(employee_timezone=employee_tz)\
                .get_work_duration_data(
                    max(date_from, contract_start),
                    min(date_to, contract_end),
                    domain=[('company_id', 'in', [False, contract.company_id.id])])
            duration_data['days'] += contract_duration_data['days']
            duration_data['hours'] += contract_duration_data['hours']
        return duration_data
