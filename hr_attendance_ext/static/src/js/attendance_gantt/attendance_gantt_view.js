/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { onWillStart } from "@odoo/owl";
import { GanttController } from "@web_gantt/gantt_controller";
import { attendanceGanttView } from "@hr_attendance_gantt/attendance_gantt/attendance_gantt_view";
import { useAttendanceEntry } from "./attendance_entry_hook";

export class AttendanceExtCalendarController extends GanttController {
    setup() {
        super.setup(...arguments);
        this.user = useService('user');
        const { onRegenerateAttendanceEntry } = useAttendanceEntry();
        this.onRegenerateAttendanceEntry = onRegenerateAttendanceEntry;
        onWillStart(async () => {
            this.showButton = await this.user.hasGroup("hr_attendance.group_hr_attendance_officer");
        });
    }

}


const attendanceGanttViewExt = {
    ...attendanceGanttView,
    Controller: AttendanceExtCalendarController,
    buttonTemplate: "hr_attendance_ext.calendar.controlButtons",
};

registry.category("views").add("attendance_gantt", attendanceGanttViewExt, { force: true });

