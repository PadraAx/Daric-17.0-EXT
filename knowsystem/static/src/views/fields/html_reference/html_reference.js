/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { HtmlField } from "@web_editor/js/backend/html_field";
import { KnowSystemFormViewDialog } from "@knowsystem/views/dialogs/knowsystem_dialog/knowsystem_dialog";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { x2ManyCommands } from "@web/core/orm_service";
const { onWillStart } = owl;
const knowSystemOptionKeys = {
    "mail.compose.message": "knowsystem_composer_option",
    "mail.activity.schedule": "knowsystem_activity_option",
}


patch(HtmlField.prototype, {
    /*
    * Re-write to get whether the current HTML model is suitable for KnowSystem
    */
    setup() {
        super.setup(...arguments);
        this.dialogService = useService("dialog");
        this.orm = useService("orm");
        this.knowsystemTurn = false;
        onWillStart(async () => { await this._checkKMSSetting(this.props) });
    },
    /*
    * The method to define whether the current HTML model is suitable for KnowSystem
    */
    async _checkKMSSetting(props) {
        const knowSystemOptionKey = knowSystemOptionKeys[props.record.resModel];
        if (knowSystemOptionKey) {
            this.knowsystemTurn = await this.orm.call("knowsystem.article", "action_check_option", [knowSystemOptionKey])
        };
    },
    /*
    * Re-write to add the KnowSystem command for the special HTML widget
    */
    get wysiwygOptions() {
        const options = super.wysiwygOptions;
        if (this.knowsystemTurn) {
            Object.assign(options, {
                KMSTurnOn: this.knowsystemTurn,
                onOpenKMSDialog: this.onOpenKMSDialog.bind(this),
            });
        };
        return options
    },
    /*
    * The method to open knowsystem search dialog and apply referencing
    */
    async onOpenKMSDialog(odooEditor, parseHTML, preserveCursor) {
        var self = this;
        const restoreSelection = preserveCursor(odooEditor.document);
        const context = {
            kms_model: this.props.record.data.model || this.props.record.data.res_model || false,
            kms_res_ids: this.props.record.data.res_ids,
        };
        this.dialogService.add(KnowSystemFormViewDialog, {
            context,
            resModel: "article.search",
            title: _t("Knowledge Base"),
            pdfAttach: this.props.record.resModel == "mail.compose.message",
            onRecordSaved: async (formRecord, params) => {
                const selectedRecords = formRecord.data.selected_article_ids.records;
                if (selectedRecords.length > 0) {
                    restoreSelection();
                    const actionResult = await this.orm.call(
                        "knowsystem.article",
                        "action_proceed_article_action",
                        [formRecord.data.selected_article_ids.currentIds, params.kmsAction],
                    );
                    if (params.kmsAction == "attach") {
                        if (actionResult && actionResult.length > 0) {
                            actionResult.forEach(function (attachment) {
                                self._onAttachmentChange(attachment);
                            });
                        };
                    }
                    else {
                        const htmlToParse = parseHTML(odooEditor.document, actionResult);
                        odooEditor.observerUnactive("commitChanges");
                        odooEditor.observerUnactive("handleSelectionInTable");
                        await odooEditor.execCommand("insert", htmlToParse);
                        odooEditor.observerActive("commitChanges");
                        odooEditor.observerActive("handleSelectionInTable");
                    };
                };
            },
            onUnmount: () => { restoreSelection() },
        });
    },
    /*
    * Re-write to fix a temporary bug of an empty id (when an image is added to email composer
    * to-do: In general, should be deleted when image uploading to emails is fixed
    */
    _onAttachmentChange(attachment) {
        if (!(this.props.record.fieldNames.includes('attachment_ids') && this.props.record.resModel === 'mail.compose.message')) {
            return;
        }
        const currentSelection = this.props.record.data.attachment_ids.currentIds || [];
        currentSelection.push(attachment.id);
        this.props.record.update({
            attachment_ids: [x2ManyCommands.set(currentSelection)]
        });
    },
});
