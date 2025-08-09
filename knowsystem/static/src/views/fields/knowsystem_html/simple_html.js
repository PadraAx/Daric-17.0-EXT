/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { getRangePosition } from "@web_editor/js/editor/odoo-editor/src/utils/utils";
import { HtmlField, htmlField } from "@web_editor/js/backend/html_field";
import { initializeTabCss } from "@knowsystem/views/fields/knowsystem_html/initialize_css";
import { loadBundle, loadJS } from "@web/core/assets";
import { toInline, getCSSRules } from "@web_editor/js/backend/convert_inline";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useSubEnv, status } from "@odoo/owl";

function stripHistoryIds(value) {
    return value && value.replace(/\sdata-last-history-steps="[^"]*?"/, '') || value;
};

export class SimpleHtml extends HtmlField {
    static props = {
        ...standardFieldProps,
        ...HtmlField.props,
        updateEditor: { type: Function, optional: false },
        getNoMoreCommit: { type: Function, optional: false },
    };
    /*
    * Re-write to avoid escess comitting
    */
    async commitChanges({ urgent } = {}) {
        if (this.props.getNoMoreCommit()) {
            return
        };
        await super.commitChanges(...arguments);
    }
    /*
    * Re-write to trigger field adaptation after the update
    */
    async updateValue() {
        const value = this.getEditingValue();
        const lastValue = (this.props.record.data[this.props.name] || "").toString();
        if (
            value !== null &&
            !(!lastValue && stripHistoryIds(value) === "<p><br></p>") &&
            stripHistoryIds(value) !== stripHistoryIds(lastValue)
        ) {
            this.props.record.model.bus.trigger("FIELD_IS_DIRTY", false);
            this.currentEditingValue = value;
            await this.props.record.update({ [this.props.name]: value });
            await this.props.updateEditor(value);
        }
    }

};
