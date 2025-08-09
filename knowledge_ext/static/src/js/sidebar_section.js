/** @odoo-module **/

import { KnowledgeSidebarSection } from "@knowledge/components/sidebar/sidebar_section";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { onWillStart } from "@odoo/owl";

patch(
    KnowledgeSidebarSection.prototype,
    {
        setup() {
            super.setup();
            this.userService = useService("user");
            onWillStart(async () => {
                this.isInternalUser = await this.userService.hasGroup('base.group_user');
                this.isSuperVisorUser = await this.userService.hasGroup('knowledge_ext.group_knowledge_supervisor');
            });
        }
    }
  );
