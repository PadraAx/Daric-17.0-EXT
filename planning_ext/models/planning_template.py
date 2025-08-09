# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import math
import pytz

from datetime import datetime, timedelta, time, date
from odoo import api, fields, models, _
from odoo.tools import format_time, float_round
from odoo.addons.resource.models.utils import float_to_time
from odoo.exceptions import ValidationError


def day_range(start: datetime, end: datetime) -> date:
    first_day = start.replace(hour=0, minute=0, second=0, microsecond=0)
    return (end - first_day).days


class PlanningTemplate(models.Model):
    _inherit = 'planning.slot.template'

    @api.depends('start_time', 'duration')
    def _compute_name(self):
        user_tz = pytz.timezone(self.env['planning.slot']._get_tz())
        today = date.today()
        for shift_template in self:
            if not 0 <= shift_template.start_time < 24:
                raise ValidationError(_('The start hour must be greater or equal to 0 and lower than 24.'))
            start_time = time(hour=int(shift_template.start_time), minute=round(
                math.modf(shift_template.start_time)[0] / (1 / 60.0)))
            start_datetime = user_tz.localize(datetime.combine(today, start_time))
            end_datetime = start_datetime + timedelta(hours=shift_template.duration)
            shift_template.end_time = timedelta(
                hours=end_datetime.hour, minutes=end_datetime.minute).total_seconds() / 3600
            shift_template.duration_days = day_range(start_datetime, end_datetime)
            end_time = time(hour=int(shift_template.end_time), minute=round(
                math.modf(shift_template.end_time)[0] / (1 / 60.0)))
            shift_template.name = '%s - %s %s' % (
                format_time(shift_template.env, start_time, time_format='HH:mm').replace(':00 ', ' '),
                format_time(shift_template.env, end_time, time_format='HH:mm').replace(':00 ', ' '),
                _('(%s days span)', shift_template.duration_days) if shift_template.duration_days > 1 else ''
            )
