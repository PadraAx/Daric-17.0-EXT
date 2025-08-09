# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError


class HrAttendanceRule(models.Model):

    _name = 'hr.attendance.rule'
    _description = 'Attendance Rule'

    name = fields.Char('name', required=True)
    code = fields.Char(required=True,
                       help="The code of salary rules can be used as reference in computation of other rules. "
                       "In that case, it is case sensitive.")
    resource_calendar_id = fields.Many2one('resource.calendar', required=True,
                                           domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    work_entry_type_id = fields.Many2one('hr.work.entry.type', 'Work Entry Type', required=True)
    work_entry_type_color = fields.Integer(related='work_entry_type_id.color')
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda self: self.env.company, readonly=True)
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(required=True, index=True, default=5,
                              help='Use to arrange calculation sequence')
    condition_formula = fields.Text(
        'Condition Formula', default='''# result = has_shift and attendance.type == 1''', required=True)
    start_formula = fields.Text(
        'Start Formula', default='''# result = max(attendance.s_date, shift.start_datetime)''', required=True)
    end_formula = fields.Text(
        'End Formula', default='''# result = min(attendance.e_date, shift.end_datetime)''', required=True)
    note = fields.Html(string='Description', translate=True)

    def _compute_formula(self, formula, localdict, source=''):
        try:
            safe_eval(formula or 0.0, localdict, mode='exec', nocopy=True)
            result = localdict['result']
        except Exception as e:
            raise UserError(_(f"""
Wrong python code defined for:{self.name}
In:  {source}
Formula: {formula}
Error: {e}
"""))
        return result

    def _compute_rule(self, localdict):
        self.ensure_one()
        localdict['localdict'] = localdict
        condition = self._compute_formula(self.condition_formula, localdict, source='condition')
        if condition:
            start = self._compute_formula(self.start_formula, localdict, source='start')
            end = self._compute_formula(self.end_formula, localdict, source='end')
            return start, end
        return False


class ResourceCalendar(models.Model):

    _inherit = 'resource.calendar'

    rule_ids = fields.One2many('hr.attendance.rule', 'resource_calendar_id', string='Rules')
