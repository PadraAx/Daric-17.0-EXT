/** @odoo-module **/

import { serializeDate } from "@web/core/l10n/dates";
import { useService } from "@web/core/utils/hooks";

export function useAttendanceEntry() {
    const orm = useService("orm");
    const action = useService("action");
    return {
        onRegenerateAttendanceEntry: () => {
            
            action.doAction('hr_attendance_ext.hr_attendance_regeneration_wizard_action', {});
        },
    }
}
