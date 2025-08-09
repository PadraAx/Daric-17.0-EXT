# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import math

from odoo import api, fields, models, _


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"

    week_end = fields.Boolean(string="WeekEnd", default=False)
