/** @odoo-module **/
/** implemented based on Odoo mass_mailing **/

import snippetsEditor from "@web_editor/js/editor/snippets.editor";


export const KnowSystemSnippetsMenu = snippetsEditor.SnippetsMenu.extend({
    custom_events: Object.assign({}, snippetsEditor.SnippetsMenu.prototype.custom_events, {
        drop_zone_over: "_onDropZoneOver",
        drop_zone_out: "_onDropZoneOut",
        drop_zone_start: "_onDropZoneStart",
        drop_zone_stop: "_onDropZoneStop",
    }),
    /*
    * Overwrite to get a correct editable zone
    */
    start: function () {
        return this._super(...arguments).then(() => {
            this.$editable = this.options.wysiwyg.getEditable();
        });
    },
    /*
    * Overwrite fix loaded img
    */
    callPostSnippetDrop: async function ($target) {
        $target.find("img[loading=lazy]").removeAttr("loading");
        return this._super(...arguments);
    },
    /*
    * Overwrite to add a dropzone
    */
    _insertDropzone: function ($hook) {
        const $hookParent = $hook.parent();
        const $dropzone = this._super(...arguments);
        $dropzone.attr("data-editor-message", $hookParent.attr("data-editor-message"));
        $dropzone.attr("data-editor-sub-message", $hookParent.attr("data-editor-sub-message"));
        return $dropzone;
    },
    // /*
    // * Overwrite to add a dropzone
    // */
    // _updateRightPanelContent: function ({content, tab}) {
    //     this._super(...arguments);
    //     this.$(".o_we_customize_design_btn").toggleClass("active", tab === this.tabs.DESIGN);
    // },
    /*
    * Handler
    */
    _onDropZoneOver: function () {
        this.$editable.find(".o_editable").css("background-color", "");
    },
    /*
    * Handler
    */
    _onDropZoneOut: function () {
        const $oEditable = this.$editable.find(".o_editable");
        if ($oEditable.find(".oe_drop_zone.oe_insert:not(.oe_vertical):only-child").length) {
            $oEditable[0].style.setProperty("background-color", "transparent", "important");
        }
    },
    /*
    * Handler
    */
    _onDropZoneStart: function () {
        const $oEditable = this.$editable.find(".o_editable");
        if ($oEditable.find(".oe_drop_zone.oe_insert:not(.oe_vertical):only-child").length) {
            $oEditable[0].style.setProperty("background-color", "transparent", "important");
        }
    },
    /*
    * Handler
    */
    _onDropZoneStop: function () {
        const $oEditable = this.$editable.find(".o_editable");
        $oEditable.css("background-color", "");
        if (!$oEditable.find(".oe_drop_zone.oe_insert:not(.oe_vertical):only-child").length) {
            $oEditable.attr("contenteditable", true);
        }
    },
    /*
    * Handler
    */
    _onSnippetRemoved: function () {
        this._super(...arguments);
        const $oEditable = this.$editable.find(".o_editable");
        if (!$oEditable.children().length) {
            $oEditable.empty(); // remove any superfluous whitespace
            $oEditable.attr("contenteditable", false);
        }
    },
});
