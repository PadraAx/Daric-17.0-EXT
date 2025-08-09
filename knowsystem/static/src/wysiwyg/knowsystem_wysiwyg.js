/** @odoo-module **/
/** implemented based on Odoo mass_mailing **/

import { loadBundle } from "@web/core/assets";
import { Wysiwyg } from "@web_editor/js/wysiwyg/wysiwyg";
import { closestElement } from "@web_editor/js/editor/odoo-editor/src/OdooEditor";
import "@web_editor/js/wysiwyg/wysiwyg_iframe";


export class KnowsystemWysiwyg extends Wysiwyg {
    /*
    * Overwrite to
    * - prevent selection change outside of snippets
    * - use the initial toolbar of the Wysiwyg as the mainToolbar
    */
    async startEdition() {
        this.mainToolbarEl = this.toolbarRef.el.firstChild;
        this.mainToolbarEl.classList.add("d-none");
        const res = await super.startEdition(...arguments);
        this.$editable.on("mousedown", e => {
            if ($(e.target).is(".o_editable:empty") || e.target.querySelector(".o_editable")) {
                e.preventDefault();
            }
        });
        this.snippetsMenuToolbarEl = this.toolbarEl;
        return res;
    }
    /*
    * Overwrite to always open the dialog when the sidebar is folded
    * and hide toolbar and avoid it being re-displayed after getDeepRange
    */
    toggleLinkTools(options = {}) {
        super.toggleLinkTools({
            ...options,
            forceDialog: options.forceDialog || this.snippetsMenu.folded
        });
        if (this.snippetsMenu.folded) {
            this.odooEditor.document.getSelection().collapseToEnd();
        }
    }
    /*
    * The method to set snippetsMenu fold state and switches toolbar
    * Configures the main toolbar if needed
    */
    setSnippetsMenuFolded(fold = true) {
        this.snippetsMenu.setFolded(fold);
        this.toolbarEl = fold ? this.mainToolbarEl : this.snippetsMenuToolbarEl;
        if (fold && !this._isMainToolbarReady) {
            this._configureToolbar({ snippets: false });
            this._updateEditorUI();
            this.setCSSVariables(this.toolbarEl);
            if (this.odooEditor.isMobile) {
                document.body.querySelector(".o_kms_body").prepend(this.toolbarEl);
            } else {
                document.body.append(this.toolbarEl);
            }
            this._isMainToolbarReady = true;
        }
        this.odooEditor.toolbar = this.toolbarEl;
        this.odooEditor.autohideToolbar = !!fold;
        this.odooEditor.toolbarHide();
        this.mainToolbarEl.classList.toggle("d-none", !fold);
    }
    /*
    * Overwrite to open the dialog in the outer document
    */
    openMediaDialog() {
        super.openMediaDialog(...arguments);
        if (this.snippetsMenu.folded) {
            this.odooEditor.toolbarHide();
        };
    }
    /*
    * Overwrite to have its own snippets editor
    */
    setValue(currentValue) {
        const initialDropZone = this.$editable[0].querySelector(".knowsystem_wrapper_td");
        const parsedHtml = new DOMParser().parseFromString(currentValue, "text/html");
        if (initialDropZone && !parsedHtml.querySelector(".knowsystem_wrapper_td")) {
            initialDropZone.replaceChildren(...parsedHtml.body.childNodes);
        } else {
            super.setValue(...arguments);
        }
    }
    /*
    * Overwrite to have its own snippets editor
    */
    async _createSnippetsMenuInstance(options={}) {
        await loadBundle("web_editor.assets_legacy_wysiwyg");
        const { KnowSystemSnippetsMenu }  = await odoo.loader.modules.get("@knowsystem/wysiwyg/snippets.editor");
        return new KnowSystemSnippetsMenu(this, Object.assign({
            wysiwyg: this,
            selectorEditableArea: ".o_editable",
        }, options));
    }
    /*
    * The method to adapt inline commands for the backend builders
    */
    _getPowerboxOptions() {
        const options = super._getPowerboxOptions();
        const {commands} = options;
        const linkCommands = commands.filter(command => command.name === 'Link' || command.name === 'Button');
        for (const linkCommand of linkCommands) {
            // Remove the command if the selection is within a background-image.
            const superIsDisabled = linkCommand.isDisabled;
            linkCommand.isDisabled = () => {
                if (superIsDisabled && superIsDisabled()) {
                    return true;
                } else {
                    const selection = this.odooEditor.document.getSelection();
                    const range = selection.rangeCount && selection.getRangeAt(0);
                    return !!range && !!closestElement(range.startContainer, '[style*=background-image]');
                }
            }
        }
        return {...options, commands};
    }
    /*
    * The method to hide the create-link button if the selection is within background-image.
    */
     _updateEditorUI(e) {
        super._updateEditorUI(...arguments);
        const selection = this.odooEditor.document.getSelection();
        if (!selection) return;
        const range = selection.rangeCount && selection.getRangeAt(0);
        const isWithinBackgroundImage = !!range && !!closestElement(range.startContainer, '[style*=background-image]');
        if (isWithinBackgroundImage) {
            this.toolbarEl.querySelector('#create-link').classList.toggle('d-none', true);
        }
    }
};
