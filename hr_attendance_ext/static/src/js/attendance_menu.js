/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ActivityMenu } from "@hr_attendance/components/attendance_menu/attendance_menu";

patch(
    ActivityMenu.prototype,
    {
        async signInOut() {
            await this.rpc("/hr_attendance/systray_check_in_out")
            await this.searchReadEmployee()
        }
    }
  );


