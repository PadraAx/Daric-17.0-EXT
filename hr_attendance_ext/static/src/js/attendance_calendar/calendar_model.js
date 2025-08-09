/** @odoo-module */

import { CalendarModel } from '@web/views/calendar/calendar_model';
import {  serializeDateTime } from "@web/core/l10n/dates";

export class AttendanceExtCalendarModel extends CalendarModel {
   
    computeRangeDomain(data) {
        const { fieldMapping } = this.meta;
        const formattedEnd = serializeDateTime(data.range.end);
        const formattedStart = serializeDateTime(data.range.start);

        const domain = [[fieldMapping.date_start, "<=", formattedEnd],[fieldMapping.date_start, ">=", formattedStart]];
        if (fieldMapping.date_stop) {
            domain.push("|");
            domain.push([fieldMapping.date_stop, "=", false]);
            domain.push([fieldMapping.date_stop, ">=", formattedStart]);
        }
        return domain;
    }

}
