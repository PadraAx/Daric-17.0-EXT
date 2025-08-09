/** @odoo-module */

import { Dialog } from "@web/core/dialog/dialog";
import { _lt } from "@web/core/l10n/translation";
import { useChildRef } from "@web/core/utils/hooks";
import { useService } from "@web/core/utils/hooks";

import { Component } from "@odoo/owl";

export class KnowledgeHtmlConfirmationDialog extends Component {
    setup() {
        this.env.dialogData.close = () => this._cancel();
        this.modalRef = useChildRef();
        this.actionService = useService("action");
        this.isConfirmedOrCancelled = false; // ensures we do not confirm and/or cancel twice
    }
    async _cancel() {
        if (this.isConfirmedOrCancelled) {
            return;
        }
        this.isConfirmedOrCancelled = true;
        this.disableButtons();
        if (this.props.cancel) {
            try {
                await this.props.cancel();
            } catch (e) {
                this.props.close();
                throw e;
            }
        }
        this.props.close();
    }
    async _confirm() {
        if (this.isConfirmedOrCancelled) {
            return;
        }
        this.isConfirmedOrCancelled = true;
        this.disableButtons();
        if (this.props.confirm) {
            try {
                await this.props.confirm();
            } catch (e) {
                this.props.close();
                throw e;
            }
        }
        this.props.close();
    }
    async _taskRequest(){
        this.actionService.doAction({
            res_model: "knowledge.request",
            res_id: this.props.id,
            views: [[false, "form"]],
            type: "ir.actions.act_window",
            view_mode: "form",
        });
        this.props.close();
    }

    disableButtons() {
        if (!this.modalRef.el) {
            return; // safety belt for stable versions
        }
        for (const button of [...this.modalRef.el.querySelectorAll(".modal-footer button")]) {
            button.disabled = true;
        }
    }
}
KnowledgeHtmlConfirmationDialog.template = "knowledge_ext.KnowledgeHtmlConfirmationDialog";
KnowledgeHtmlConfirmationDialog.components = { Dialog };
KnowledgeHtmlConfirmationDialog.props = {
    close: Function,
    title: {
        validate: (m) => {
            return (
                typeof m === "string" || (typeof m === "object" && typeof m.toString === "function")
            );
        },
        optional: true,
    },
    body: String,
    confirm: { type: Function, optional: true },
    confirmLabel: { type: String, optional: true },
    cancel: { type: Function, optional: true },
    cancelLabel: { type: String, optional: true },
    id: { type: Number, optional: true},
    showButton: { type: Boolean, optional: true },
    ViewTaskLabel: { type: String, optional: true },
};
KnowledgeHtmlConfirmationDialog.defaultProps = {
    confirmLabel: _lt("Ok"),
    cancelLabel: _lt("Cancel"),
    showButton:false,
    title: _lt("Confirmation"),
    ViewTaskLabel:'View Task'
};

export class KnowledgeHtmlAlertDialog extends KnowledgeHtmlConfirmationDialog {}
KnowledgeHtmlAlertDialog.template = "knowledge_ext.KnowledgeHtmlAlertDialog";
KnowledgeHtmlAlertDialog.props = {
    ...KnowledgeHtmlConfirmationDialog.props,
    contentClass: { type: String, optional: true },
};
KnowledgeHtmlAlertDialog.defaultProps = {
    ...KnowledgeHtmlConfirmationDialog.defaultProps,
    title: _lt("Alert"),
};
