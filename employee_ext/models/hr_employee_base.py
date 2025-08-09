# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval

from pytz import timezone, UTC, utc
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import format_time


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"


    parent_id = fields.Many2one('hr.employee', 'Manager', compute=False, store=True, readonly=False, check_company=True)
    tz = fields.Selection(string='Timezone', related='resource_id.tz', readonly=False, tracking=True,
                            help="This field is used in order to define in which timezone the resources will work.")
    sit_taker = fields.Selection(string='Seat Taker', selection=[('yes', 'Yes'),
                                                                ('no', 'No')], required=True, tracking=True)


    @api.depends('department_id')
    def _compute_parent_id(self):
        # over write to prevent error on edit parent_id
        pass


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"


    sit_taker = fields.Selection(readonly=True)