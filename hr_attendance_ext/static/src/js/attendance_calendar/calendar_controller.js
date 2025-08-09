/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { CalendarController } from "@web/views/calendar/calendar_controller";
import { FormViewDialog } from "@web/views/view_dialogs/form_view_dialog";
// import { serializeDate } from "@web/core/l10n/dates";
import { AttendanceExtFormViewDialog } from "../view_dialog/form_view_dialog";



export class AttendanceExtCalendarController extends CalendarController {
 
    async editRecord(record, context = {}, shouldFetchFormViewId = true) {
        const onDialogClosed = () => {
            this.model.load();
        };

        return new Promise((resolve) => {
            this.displayDialog(
                AttendanceExtFormViewDialog,
                {
                    resModel: this.model.resModel,
                    resId: record.id || false,
                    context,
                    title: record.title,
                    viewId: this.model.formViewId,
                    onRecordSaved: onDialogClosed,
                    onRecordDeleted: (record) => this.deleteRecord(record),
                    // close: (record) => this.close(record),
                    size: "md",
                },
                { onClose: () => resolve() }
            );
        });
    }

    newAttendanceRequest() {
        const context = {};
        // if (this.employeeId) {
        //     context["default_employee_id"] = this.employeeId;
        // }
        // if (this.model.meta.scale == "day") {
        //     context["default_date_from"] = serializeDate(
        //         this.model.data.range.start.set({ hours: 7 }),
        //         "datetime"
        //     );
        //     context["default_date_to"] = serializeDate(
        //         this.model.data.range.end.set({ hours: 19 }),
        //         "datetime"
        //     );
        // }

        this.displayDialog(FormViewDialog, {
            resModel: "hr.attendance",
            title: _t("New Attendance"),
            viewId: this.model.formViewId,
            onRecordSaved: () => {
                this.model.load();
                // this.env.timeOffBus.trigger("update_dashboard");
            },
            context: context,
        });
    }

}

AttendanceExtCalendarController.components = {
    ...AttendanceExtCalendarController.components,
};

AttendanceExtCalendarController.template = "hr_attendance_ext.CalendarController";
