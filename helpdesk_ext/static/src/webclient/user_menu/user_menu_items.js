/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";

function odooAccountItemExt(env) {
    const baseUrl = window.location.origin;
    const dynamicUrl = `${baseUrl}/my/home`;

    return {
        type: "item",
        id: "account",
        description: _t("Portal Account"),
        callback: () => {
            env.services
                .rpc("/web/session/account")
                .then(() => {
                    browser.open(dynamicUrl, "_blank");
                })
                .catch(() => {
                    browser.open(dynamicUrl, "_blank");
                });
        },
        sequence: 60,
    };
}

// Ensure both items are fully removed before adding the custom one
registry.category("user_menuitems").remove("odoo_account");
registry.category("user_menuitems").remove("settings");  // Removes "Preferences"
registry.category("user_menuitems").remove("preferences"); // Some versions use this ID
registry.category("user_menuitems").add("odoo_account", odooAccountItemExt);
