# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResourceCalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"
    _description = "Resource Time Off Detail"
    _order = "date_from desc"


    name = fields.Char('Name', required=True, tracking=True)
    date_to = fields.Datetime('End Date', required=True, tracking=True)


    @api.onchange('date_from')
    def _compute_date_to(self):
        for leave in self:
            if leave.date_from:
                leave.date_to = leave.date_from
