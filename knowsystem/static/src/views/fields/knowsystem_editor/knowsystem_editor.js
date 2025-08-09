/** @odoo-module **/

import { _lt } from "@web/core/l10n/translation";
import { AceField } from "@web/views/fields/ace/ace_field";
import { browser } from "@web/core/browser/browser";
import { KnowSystemHtml } from "@knowsystem/views/fields/knowsystem_html/knowsystem_html";
import { SimpleHtml } from "@knowsystem/views/fields/knowsystem_html/simple_html";
import { HtmlField, htmlField } from "@web_editor/js/backend/html_field";
import { TextField } from "@web/views/fields/text/text_field";
import { Tooltip } from "@web/core/tooltip/tooltip";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";
const { onWillStart, onWillUpdateProps } = owl;


export class KnowSystemEditor extends HtmlField {
    static template = "knowsystem.KnowSystemEditor";
    static components = {
        ...HtmlField.components,
        AceField,
        KnowSystemHtml,
        SimpleHtml,
        HtmlField,
        TextField,
    };
    /*
    * Re-write to introduce our own services and action
    */
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.userService = useService("user");
        this.popover = useService("popover");
        this._makeReadonly();
        onWillStart(async () => {
            const proms = [
                this._loadSettings(this.props),
                this._updateNumberOfViews(false)
            ];
            return Promise.all(proms);
        });
        onWillUpdateProps(async (nextProps) => {
            const proms = [
                this._loadSettings(nextProps),
                this._updateNumberOfViews(nextProps),
            ];
            return Promise.all(proms);
        });
    }
    /*
    * Re-write to avoid standard field comitting but postprocess values of all the types except the backend editor
    */
    async commitChanges() {
        if ((this.state.editorType != "backend_editor" && this.state.editorType != "html") || this.state.aceEditor) {
            console.log("OUR commitChanges")
            await this._updateEditor(this.props.record.data.description_arch)
        };
    }
    /*
    * The method to load props available in readonly mode
    */
    _getReadonlyProps() {
        var props = { };
        Object.assign(props, this.props, {
            name: this.state.editorType == "text" ? "description" : "description_arch",
            readonly: true,
        });
        if (this.state.editorType == "backend_editor" || this.state.editorType == "website_editor") {
            const editorAssets = this.state.editorType == "backend_editor" ? "knowsystem.iframe_css_assets_edit" : "knowsystem.iframe_css_assets_edit_website";
            var wysiwygOptions = {};
            Object.assign(wysiwygOptions, this.props.wysiwygOptions, {
                iframeCssAssets: editorAssets,
                iframeHtmlClass: "knowsystem_iframe",
                inIframe: true,
            });
            Object.assign(props, {
                cssReadonlyAssetId: editorAssets,
                wysiwygOptions: wysiwygOptions,
            });
        };
        return props
    }
    /*
    * The method to get props for the target field type
    */
    _getEditProps() {
        const props = { };
        if (this.state.aceEditor) {
            const aceFieldProps = Object.keys(standardFieldProps);
            for (const [key, value] of Object.entries(this.props)) {
                if (aceFieldProps.includes(key)) { props[key] = value };
            };
        }
        else {
            if (this.state.editorType == "backend_editor") {
                var wysiwygOptions = {};
                Object.assign(wysiwygOptions, this.props.wysiwygOptions, {
                    snippets: "knowsystem.knowsystem_snippets",
                    inIframe: true,
                    iframeCssAssets: "knowsystem.iframe_css_assets_edit",
                    iframeHtmlClass: "knowsystem_iframe",
                });
                wysiwygOptions.mediaModalParams.noVideos = false;
                Object.assign(props, this.props, {
                    dynamicPlaceholder: true,
                    cssReadonlyAssetId: "knowsystem.iframe_css_assets_edit",
                    wysiwygOptions: wysiwygOptions,
                    aceMode: this.state.aceMode,
                    updateEditor: this._updateEditor.bind(this),
                    getNoMoreCommit: this.getNoMoreCommit.bind(this),
                });
            }
            else if (this.state.editorType == "html") {
                Object.assign(props, this.props, {
                    updateEditor: this._updateEditor.bind(this),
                    getNoMoreCommit: this.getNoMoreCommit.bind(this),
                });
            }
            else if (this.state.editorType == "text") {
                const textFieldProps = Object.keys(standardFieldProps).concat(["isTranslatable", "placeholder", "dynamicPlaceholder"]);
                for (const [key, value] of Object.entries(this.props)) {
                    if (textFieldProps.includes(key)) { props[key] = value };
                };
            };
        };
        return props
    }
    /*
    * The method to update number of views each time content is initiated
    */
    async _updateNumberOfViews(props) {
        if (this.props.record.resModel != "knowsystem.article") { return };
        if (!props || props.record.data.id != this.props.record.data.id) {
            const recordId = props ? props.record.data.id : this.props.record.data.id;
            await this.orm.call("knowsystem.article", "action_update_number_of_views", [recordId])
        };
    }
    /*
    * The method to load the initial settings
    */
    async _loadSettings(props) {
        if (props.record.data.id != this.state.recordId) {
            this._keepInitial(props);
        };
        const editorsTypes = await this.orm.call("knowsystem.article", "action_get_editor_types", []);
        const websiteEditor = await this.userService.hasGroup("website.group_website_restricted_editor");
        Object.assign(this.state, {
            editorType: props.record.data.editor_type,
            editorsTypes: editorsTypes,
            websiteEditor: websiteEditor,
            recordId: props.record.data.id,
        });
    }
    /*
    * The method to change the editor type
    */
    async _onChangeEditor(event) {
        this.state.editorType = event.currentTarget.value;
        this._updateRecord({ editor_type : this.state.editorType })
    }
    /*
    * The method to open the ace editor of the article
    */
    onOpenAceEditor() {
        this._keepInitial(this.props);
        Object.assign(this.state, { readonly: false, aceEditor: true });
    }
    /*
    * The method to open the correct editor (field type based on the type)
    */
    async onSwitchEdit() {
        this._keepInitial(this.props);
        Object.assign(this.state, { readonly: false, aceEditor: false });
    }
    /*
    * The method to close the editor and save
    */
    async onSwitchReadOnly() {
        const saved = await this.props.record.save();
        if (saved) {
            this._makeReadonly();
        };
    }
    /*
    * The method to rollback the initial value
    */
    async onDiscardEdit() {
        this.noMoreCommit = true;
        await this._updateRecord({
            description_arch: this.initialDescriptionArch, description: this.initialDescription,
        });
        await this.onSwitchReadOnly();
        this.noMoreCommit = false;
    }
    /*
    * Just an extra check to avoid excess commites
    */
    getNoMoreCommit() {
        return this.state.readonly || this.noMoreCommit;
    }
    /*
    * The method to put description (not description_arch) to clipboard
    */
    async onCopy() {
        const popoverEl = $(event.target).closest("div");
        var popoverTooltip = _lt("Successfully copied!"),
            popoverClass = "text-success",
            popoverTimer = 800;
        try {
            await navigator.clipboard.writeText([this.props.record.data.description]);
            // at the moment HTML support is too limited to introduce that
            // const blob = new Blob([content], { type: "text/html" });
            // const richTextInput = new ClipboardItem({ "text/html": blob });
            // await navigator.clipboard.write([richTextInput]);
        } catch {
            popoverTooltip = _lt("Error! This browser doesn't allow to copy to clipboard");
            popoverClass = "text-danger";
            popoverTimer = 2500;
        };
        if (popoverEl.length != 0) {
            const closeTooltip = this.popover.add(
                popoverEl[0],
                Tooltip,
                { tooltip: popoverTooltip },
                { popoverClass: popoverClass, }
            );
            browser.setTimeout(() => { closeTooltip() }, popoverTimer);
        }
    }
    /*
    * The method to save changes of description arch to description when it is updated
    */
    async _updateEditor(value, getReadonly) {
        var descriptionVal = value;
        var aceEditorPostProcess = false, needUpdate = false;
        if (descriptionVal && descriptionVal != "") {
            if (getReadonly) {
                descriptionVal = await getReadonly();
            }
            else if (this.state.aceEditor && this.state.editorType == "backend_editor") {
                aceEditorPostProcess = true;
            }
            else if (this.state.editorType == "text") {
                descriptionVal = descriptionVal.replace(/\n/g, "<br />");
            };
        };
        if (aceEditorPostProcess) {
            // for the ace editor of the backend editor we need to postprocess description_arch using the backend field
            if (value != this.props.record.data.description_arch) {
                this.state.aceMode = true;
                await this.onSwitchEdit();
                await this._updateRecord( { description_arch: value });
            };
        }
        else {
            if (this.state.aceMode || this.lastValueArch != value || this.lastValueVal != descriptionVal) {
                await this._updateRecord( { description_arch: value, description: descriptionVal } );
                this.state.aceMode = false;
            };
            this.lastValueArch = value;
            this.lastValueVal = descriptionVal;
        };
        this.props.record.model.bus.trigger("FIELD_IS_DIRTY", false);
    }
    /*
    * The method to update the record
    */
    async _updateRecord(changes) {
        await this.props.record.update(changes);
    }
    /*
    * The method to make the field readonly
    */
    _makeReadonly() {
        Object.assign(this.state, { readonly: true, aceEditor: false });
    }
    /*
    * The method to save the initial values
    */
    _keepInitial(props) {
        this.initialDescriptionArch = props.record.data.description_arch;
        this.initialDescription = props.record.data.description;
    }
};

export const knowSystemEditor = { ...htmlField, component: KnowSystemEditor };

registry.category("fields").add("knowsystemEditor", knowSystemEditor, { force: true });
