/** @odoo-module **/
import { X2ManyField, x2ManyField } from "@web/views/fields/x2many/x2many_field";
import {
    useX2ManyCrud,
    useOpenX2ManyRecord,
} from "@web/views/fields/relational_utils";
import { registry } from "@web/core/registry";
import { useService } from '@web/core/utils/hooks';
import { ListRenderer } from "@web/views/list/list_renderer";
//CommonSkillsListRenderer
export class RowNoListRenderer extends ListRenderer {
    setup() {
        super.setup();
        this.orm = useService('orm');
        this.action = useService("action");
        this.actionService = useService("action");
    }
    // get colspan() {
    //     const span = this.allColumns.length;
    //     if (this.isEditable) {
    //         return span + 1;
    //     }

    //     return span;
    // }

    // freezeColumnWidths() {
    //     if (!this.keepColumnWidths) {
    //         this.columnWidths = null;
    //     }
    //     const table = this.tableRef.el;
    //     const headers = [...table.querySelectorAll("thead th:not(.o_list_actions_header)")];
    //     this.setDefaultColumnWidths();
    //     if (!this.columnWidths || !this.columnWidths.length) {
    //         // no column widths to restore

    //         table.style.tableLayout = "fixed";
    //         const allowedWidth = table.parentNode.getBoundingClientRect().width;
    //         // Set table layout auto and remove inline style to make sure that css
    //         // rules apply (e.g. fixed width of record selector)
    //         table.style.tableLayout = "auto";
    //         headers.forEach((th) => {
    //             th.style.width = null;
    //             th.style.maxWidth = null;
    //         });
    //         this.setDefaultColumnWidths();
    //         // Squeeze the table by applying a max-width on largest columns to
    //         // ensure that it doesn't overflow
    //         this.columnWidths = this.computeColumnWidthsFromContent(allowedWidth);
    //         table.style.tableLayout = "fixed";
    //     }
    //     headers.forEach((th, index) => {
    //         if (!th.style.width) {
    //             th.style.width = `${Math.floor(this.columnWidths[index])}px`;
    //         }
    //     });

    // }
    setDefaultColumnWidths() {
        const widths = this.state.columns.map((col) => this.calculateColumnWidth(col));
        const sumOfRelativeWidths = widths
            .filter(({ type }) => type === "relative")
            .reduce((sum, { value }) => sum + value, 0);

        // 1 because nth-child selectors are 1-indexed, 2 when the first column contains
        // the checkboxes to select records.
        // const columnOffset = this.hasSelectors ? 2 : 1;
        const columnOffset = 2;
        widths.forEach(({ type, value }, i) => {

            const headerEl = this.tableRef.el.querySelector(`th:nth-child(${i + columnOffset})`);
            if (type === "absolute") {
                if (this.isEmpty) {
                    headerEl.style.width = value;
                } else {
                    headerEl.style.minWidth = value;
                }
            } else if (type === "relative" && this.isEmpty) {
                headerEl.style.width = `${((value / (sumOfRelativeWidths)) * 100).toFixed(2)}%`;
            }
        });
    }

}
RowNoListRenderer.defaultProps = { hasSelectors: true, cycleOnTab: true };
RowNoListRenderer.template = 'rowno_in_tree.RowNoFieldListRenderer';
RowNoListRenderer.rowsTemplate = "rowno_in_tree.RowNoFieldListRenderer.Rows";
RowNoListRenderer.recordRowTemplate = "rowno_in_tree.RowNoFieldListRenderer.RecordRow";
//SkillsX2ManyField
export class RowNo_X2ManyField extends X2ManyField {
    setup() {
        super.setup()
        const { saveRecord, updateRecord } = useX2ManyCrud(
            () => this.list,
            this.isMany2Many
        );

        const openRecord = useOpenX2ManyRecord({
            resModel: this.list.resModel,
            activeField: this.activeField,
            activeActions: this.activeActions,
            getList: () => this.list,
            saveRecord: async (record) => {
                await saveRecord(record);
                await this.props.record.save();
            },
            updateRecord: updateRecord,
            withParentId: this.props.widget !== "many2many",
        });
    }
}

RowNo_X2ManyField.components = {
    ...X2ManyField.components,
    ListRenderer: RowNoListRenderer,
};

export const rowNo_X2ManyField = {
    ...x2ManyField,
    component: RowNo_X2ManyField,
};

registry.category("fields").add("rowno_one2many", rowNo_X2ManyField);