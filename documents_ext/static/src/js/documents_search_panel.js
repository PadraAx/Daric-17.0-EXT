/** @odoo-module **/

import {DocumentsSearchPanel} from "@documents/views/search/documents_search_panel";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { browser } from "@web/core/browser/browser";
import { SearchPanel } from "@web/search/search_panel/search_panel";
import { useNestedSortable } from "@web/core/utils/nested_sortable";
import { usePopover } from "@web/core/popover/popover_hook";
import { useService } from "@web/core/utils/hooks";
import { utils as uiUtils } from "@web/core/ui/ui_service";
import { Component, onWillStart, useState } from "@odoo/owl";
import { toggleArchive } from "@documents/views/hooks";

const VALUE_SELECTOR = [".o_search_panel_category_value", ".o_search_panel_filter_value"].join();
const FOLDER_VALUE_SELECTOR = ".o_search_panel_category_value";
const LONG_TOUCH_THRESHOLD = 400;

/**
 * This file defines the DocumentsSearchPanel component, an extension of the
 * SearchPanel to be used in the documents kanban/list views.
 */

export class DocumentsSearchPanelItemSettingsPopover extends Component {
    static props = [
        "close", // Function, close the popover
        "createChildEnabled", // Whether we have the option to create a new child or not
        "onCreateChild", // Function, create new child
        "onEdit", // Function, edit element
    ];
}
DocumentsSearchPanelItemSettingsPopover.template =
    "documents.DocumentsSearchPanelItemSettingsPopover";
    
patch(DocumentsSearchPanel.prototype, {

    setup() {
        super.setup(...arguments);
        const { uploads } = useService("file_upload");
        this.documentUploads = uploads;
        useState(uploads);
        this.notification = useService("notification");
        this.orm = useService("orm");
        this.user = useService("user");
        this.action = useService("action");
        this.popover = usePopover(DocumentsSearchPanelItemSettingsPopover, {
            onClose: () => this.onPopoverClose?.(),
            popoverClass: "o_search_panel_item_settings_popover",
        });
        this.dialog = useService("dialog");

        onWillStart(async () => {
            debugger;
           const manager = await this.user.hasGroup("documents.group_documents_manager");
           const administrator =await this.user.hasGroup("documents_ext.group_documents_workspace_administrator");
           if (manager || administrator)
                this.isDocumentManager =true;
            else 
                 this.isDocumentManager =false;

        });

        useNestedSortable({
            ref: this.root,
            groups: ".o_search_panel_category",
            elements: "li:not(.o_all_or_trash_category)",
            enable: () => this.isDocumentManager,
            nest: true,
            nestInterval: 10,
            /**
             * When the placeholder moves, unfold the new parent and show/hide carets
             * where needed.
             * @param {DOMElement} parent - parent element of where the element was moved
             * @param {DOMElement} newGroup - group in which the element was moved
             * @param {DOMElement} prevPos.parent - element's parent before the move
             * @param {DOMElement} placeholder - hint element showing the current position
             */
            onMove: ({ parent, newGroup, prevPos, placeholder }) => {
                if (parent) {
                    parent.classList.add("o_has_treeEntry");
                    placeholder.classList.add("o_treeEntry");
                    const parentSectionId = parseInt(newGroup.dataset.sectionId);
                    const parentValueId = parseInt(parent.dataset.valueId);
                    this.state.expanded[parentSectionId][parentValueId] = true;
                } else {
                    placeholder.classList.remove("o_treeEntry");
                }
                if (prevPos.parent && !prevPos.parent.querySelector("li")) {
                    prevPos.parent.classList.remove("o_has_treeEntry");
                }
            },
            onDrop: async ({ element, parent, next }) => {
                const draggingFolderId = parseInt(element.dataset.valueId);
                const parentFolderId = parent ? parseInt(parent.dataset.valueId) : false;
                const beforeFolderId = next ? parseInt(next.dataset.valueId) : false;
                await this.orm.call("documents.folder", "move_folder_to", [
                    [draggingFolderId],
                    parentFolderId,
                    beforeFolderId,
                ]);
                await this._reloadSearchModel(true);
            },
        });
    },

});
