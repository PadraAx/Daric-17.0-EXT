/** @odoo-module */

import { formatDateTime, parseDateTime } from "@web/core/l10n/dates";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks"
const { Component, onRendered, useState } = owl;


export class RevisionsTable extends Component {
    static template = "knowsystem.RevisionsTable";
    static props = { ...standardFieldProps };
    /*
    * Overwrite to introduce our own services
    */
    setup() {
        this.orm = useService("orm");
        this.state = useState({ revisionsList: null, allRecordsLen: 0 });
        this.actionService = useService("action");
        onRendered(async () => {
            // We recalc on each render instead of onwillstart/onupdate props to make sure it is updated on any change
            await this._loadRevisions(this.props);
        });
    }
    /*
    * The method to load revisions data
    */
    async _loadRevisions(props) {
        const records = props.record.data[props.name].records;
        if (this.state.revisionsList) {
            console.log("this.state.revisionsList.length", this.state.revisionsList.length);
        };
        if (!this.state.revisionsList || records.length != this.state.allRecordsLen) {
            const recordIds = records.map((record) => record.data.id);
            const revisionsList = await this.orm.call(
                "knowsystem.article.revision", "action_get_revisions", [recordIds],
            );
            Object.assign(this.state, {
                revisionsList: this._preprocessRevisions(revisionsList),
                allRecordsLen: records.length, // it might be different from revisionsList because of the lang
            });
        };
    }
    /*
    * The method to preprocess record data before showing
    */
    _preprocessRevisions(revisionsList) {
        return revisionsList.map(m => ({
            ...m,
            published_date_str:
                formatDateTime(
                    parseDateTime(
                        m.change_datetime,
                        { format: 'MM-dd-yyy HH:mm:ss' },
                    ),
                )
        }));
    }
    /*
    * The method to execute action of showing the revision
    */
    async onObserve(revisionId) {
        await this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "knowsystem.article.revision",
            res_id: revisionId,
            views: [[false, "form"]],
        });
    }
};

export const revisionsTable = {
    component: RevisionsTable,
    supportedTypes: ["many2many"],
    relatedFields: [ { name: "id", type: "integer" } ],
};

registry.category("fields").add("revisionsTable", revisionsTable);
