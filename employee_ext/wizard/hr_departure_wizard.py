# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.exceptions import ValidationError


class HrDepartureWizard(models.TransientModel):
    _inherit = 'hr.departure.wizard'


    def _get_employee_termination_date(self):
        return self.env['hr.employee'].browse(self.env.context['active_id']).termination_date

    def _get_default_termination_date(self):
        termination_date = False
        if self.env.context.get('active_id'):
            termination_date = self._get_employee_termination_date()
        return termination_date or fields.Date.today()


    set_date_end = fields.Boolean(string="Set Contract End Date", default=False, help="Set the end date on the current contract.")
    apply_contr_end_date = fields.Boolean(string="Contract", default=True, help="Set the end date on the current contract.")
    termination_date = fields.Date('Termination Date', tracking=True, default=_get_default_termination_date)


    def action_register_departure(self):
        employee = self.employee_id
        if len(employee.child_ids) > 0:
            raise ValidationError(_("You cannot archive employee who has subordinates because their managers will be empty."))
        current_contract = self.sudo().employee_id.contract_ids.filtered(lambda l: l.state == 'open')
        super(HrDepartureWizard, self).action_register_departure()
        employee.termination_date = self.termination_date
        if self.apply_contr_end_date and current_contract:
            for contract in current_contract:
                contract.sudo().write({'date_end': self.departure_date})
        employee.work_location_id = False
        employee.address_id = False
