/** @odoo-module */

import { FormViewDialog } from "@web/views/view_dialogs/form_view_dialog";

import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";

import { formView } from '@web/views/form/form_view';
import { FormController } from '@web/views/form/form_controller';


export class AttendanceExtDialogFormController extends FormController {
    setup() {
        super.setup();
        this.orm = useService("orm");
    }

    async onClick(action) {
        console.log("click_ha");
        
        const args = [this.record.resId];
        await this.orm.call("hr.attendance", action, args);
    }

    get record() {
        return this.model.root;
    }

    deleteRecord() {
        debugger;
        this.props.onRecordDeleted(this.record);
        // this.props.close();
    }

    get canDelete() {
        return !this.model.root.isNew;
    }

}

AttendanceExtDialogFormController.props = {
    ...FormController.props,
    onRecordDeleted: Function,
}

registry.category('views').add('attendance_ext_dialog_form', {
    ...formView,
    Controller: AttendanceExtDialogFormController,
});


export class AttendanceExtFormViewDialog extends FormViewDialog {
    setup() {
        super.setup();
        this.viewProps = Object.assign(this.viewProps, {
            type: "attendance_ext_dialog_form",
            buttonTemplate: 'hr_attendance_ext.FormViewDialog.buttons',
            onRecordDeleted: (record) => {
                this.props.onRecordDeleted(record)
            },
        })
    }
}
AttendanceExtFormViewDialog.props = {
    ...AttendanceExtFormViewDialog.props,
    onRecordDeleted: Function,
}
