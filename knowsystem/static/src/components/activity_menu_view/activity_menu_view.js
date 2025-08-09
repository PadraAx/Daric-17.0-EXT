/** @odoo-module **/

import { ActivityMenu } from "@mail/core/web/activity_menu";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
const { onWillStart } = owl;


patch(ActivityMenu.prototype, {
    /*
    * Re-write to define whether the quick create option should be shown
    */
    setup() {
        this.orm = useService("orm");
        onWillStart(async () => {
            this.kmsQuickCreate = await this.orm.call("knowsystem.article", "action_check_quick_creation", []);
        });
        super.setup();
    },
    /*
    * The method to create a new article by request
    */
    async onClickNewArticles(ev) {
        document.body.click(); // hack to close dropdown
        await this.env.services.action.doAction("knowsystem.knowsystem_article_action_form_only", {});
    },
});
