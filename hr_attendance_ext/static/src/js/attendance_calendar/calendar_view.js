/** @odoo-module */

import { calendarView } from '@web/views/calendar/calendar_view';

import { AttendanceExtCalendarController } from './calendar_controller';
import { AttendanceExtCalendarModel } from './calendar_model';

import { registry } from '@web/core/registry';

const AttendanceExtCalendarView = {
    ...calendarView,
    Controller: AttendanceExtCalendarController,
    Model: AttendanceExtCalendarModel,
}

registry.category('views').add('attendance_ext_calendar', AttendanceExtCalendarView);
// registry.category('views').add('time_off_calendar_dashboard', {
//     ...TimeOffCalendarView,
//     Renderer: TimeOffDashboardCalendarRenderer,
// });
