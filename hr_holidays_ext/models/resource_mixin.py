# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from pytz import utc

from odoo import api, fields, models
from odoo.addons.resource.models.utils import timezone_datetime


class ResourceMixin(models.AbstractModel):
    _inherit = "resource.mixin"

    def list_work_time_per_day(self, from_datetime, to_datetime, calendar=None, domain=None):
        """
            By default the resource calendar is used, but it can be
            changed using the `calendar` argument.

            `domain` is used in order to recognise the leaves to take,
            None means default value ('time_type', '=', 'leave')

            Returns a list of tuples (day, hours) for each day
            containing at least an attendance.
        """
        resource = self.resource_id
        calendar = calendar or self.resource_calendar_id or self.company_id.resource_calendar_id

        # naive datetimes are made explicit in UTC
        if not from_datetime.tzinfo:
            from_datetime = from_datetime.replace(tzinfo=utc)
        if not to_datetime.tzinfo:
            to_datetime = to_datetime.replace(tzinfo=utc)

        compute_leaves = self.env.context.get('compute_leaves', True)
        calc_weekends = self.env.context.get('calc_weekends')
        intervals = calendar.with_context(calc_weekends=calc_weekends)._work_intervals_batch(from_datetime,
                                                                                             to_datetime,
                                                                                             resource,
                                                                                             domain,
                                                                                             compute_leaves=compute_leaves)[resource.id]
        result = defaultdict(float)
        for start, stop, meta in intervals:
            result[start.date()] += (stop - start).total_seconds() / 3600
        return sorted(result.items())

    def _get_work_days_data_batch(self, from_datetime, to_datetime, compute_leaves=True, calendar=None, domain=None):
        """
            By default the resource calendar is used, but it can be
            changed using the `calendar` argument.

            `domain` is used in order to recognise the leaves to take,
            None means default value ('time_type', '=', 'leave')

            Returns a dict {'days': n, 'hours': h} containing the
            quantity of working time expressed as days and as hours.
        """
        resources = self.mapped('resource_id')
        mapped_employees = {e.resource_id.id: e.id for e in self}
        result = {}

        # naive datetimes are made explicit in UTC
        from_datetime = timezone_datetime(from_datetime)
        to_datetime = timezone_datetime(to_datetime)

        mapped_resources = defaultdict(lambda: self.env['resource.resource'])
        for record in self:
            mapped_resources[calendar or record.resource_calendar_id] |= record.resource_id

        calc_weekends = self.env.context.get('calc_weekends')

        for calendar, calendar_resources in mapped_resources.items():
            if not calendar:
                for calendar_resource in calendar_resources:
                    result[calendar_resource.id] = {'days': 0, 'hours': 0}
                continue

            # actual hours per day
            if compute_leaves:
                intervals = calendar._work_intervals_batch(from_datetime, to_datetime, calendar_resources, domain)
            else:
                intervals = calendar.with_context(calc_weekends=calc_weekends)._attendance_intervals_batch(
                    from_datetime,
                    to_datetime,
                    calendar_resources)

            for calendar_resource in calendar_resources:
                result[calendar_resource.id] = calendar._get_attendance_intervals_days_data(
                    intervals[calendar_resource.id])

        # convert "resource: result" into "employee: result"
        return {mapped_employees[r.id]: result[r.id] for r in resources}
