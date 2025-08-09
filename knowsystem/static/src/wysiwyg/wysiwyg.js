/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { parseHTML, preserveCursor } from "@web_editor/js/editor/odoo-editor/src/OdooEditor";
import { Wysiwyg } from "@web_editor/js/wysiwyg/wysiwyg";


patch(Wysiwyg.prototype, {
    /*
    * Re-write to add KnowSystem command if required
    */
    _getPowerboxOptions() {
        const { commands, categories } = super._getPowerboxOptions(...arguments);
        if (this.options.KMSTurnOn) {
            commands.push({
                category: _t("Basic blocks"),
                name: _t("KnowSystem"),
                priority: 300,
                description: _t("Knowledge Base"),
                fontawesome: "fa-superpowers",
                callback: () => { this.options.onOpenKMSDialog(this.odooEditor, parseHTML, preserveCursor) },
            })
        }
        return { commands, categories };
    },

});
