/** @odoo-module **/

import { KanbanRecord } from "@web/views/kanban/kanban_record";
import { x2ManyCommands } from "@web/core/orm_service";


export class ArticleSearchKanbanRecord extends KanbanRecord {
    /*
    * The method to manage clicks on kanban record > add to selection always
    */
    async onGlobalClick(ev) {
        if (ev.target.closest("a.fa-plus-circle")) {
            // we have to use x2ManyCommands.set instead of link since selected kanban then is shown incorrect
            const currentSelection = this.props.record.model.root.data.selected_article_ids.currentIds || [];
            currentSelection.push(this.props.record.resId);
            await this.props.record.model.root.update({
                selected_article_ids: [x2ManyCommands.set(currentSelection)]
            });
        }
        else { super.onGlobalClick(ev) }
    }
};
