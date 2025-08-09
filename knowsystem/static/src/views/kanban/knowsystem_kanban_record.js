/** @odoo-module **/

import { KanbanRecord } from "@web/views/kanban/kanban_record";
const notGlobalActions = ["a", ".dropdown", ".oe_kanban_action", ".jstr-kanban-copy"].join(",");


export class KnowSystemKanbanRecord extends KanbanRecord {
    /*
    * Re-write to add its own classes for selected kanban record
    */
    getRecordClasses() {
        let result = super.getRecordClasses();
        if (this.props.record.selected) {
            result += " jstr-kanban-selected";
        };
        return result += " w-100";
    }
    /*
    * The method to manage clicks on kanban record
    */
    onGlobalClick(ev) {
        if (ev.target.closest(notGlobalActions)) {
            return;
        }
        else if (ev.target.closest(".jstr-kanban-select-box")) {
            this.props.record.onRecordClick(ev, {});
        }
        else {
            const { openRecord, record } = this.props;
            openRecord(record);
        }
    }
};
