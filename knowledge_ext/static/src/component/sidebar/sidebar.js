/** @odoo-module **/

import { KnowledgeSidebar } from "@knowledge/components/sidebar/sidebar";
import { patch } from "@web/core/utils/patch";

patch(
    KnowledgeSidebar.prototype,
    {
        async onWillStart() {
            await super.onWillStart();
            this.isSuperVisorUser = await this.userService.hasGroup('knowledge_ext.group_knowledge_supervisor');
        }
    }
  );
