/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";
const { Component } = owl;


export class FavoriteButtonField extends Component {
    static template = "knowsystem.FavoriteButtonField";
    static props = { ...standardFieldProps };
    /*
    * Re-write to add own services and actions
    */
    setup() {
        this.orm = useService("orm");
        super.setup(...arguments);
    }
    /*
    * The method to toggle favorite
    */
    async toggleFavorite() {
        if (this.props.record.data.id) {
            const thisUserFavorite = await this.orm.call(
                "knowsystem.article", "action_toggle_favorite", [[this.props.record.data.id]],
            );
            await this.props.record.update({ [this.props.name]: thisUserFavorite });
            this.props.record.save();
        }
    }
};

export const favoriteButtonField = { component: FavoriteButtonField, supportedTypes: ["boolean"] };

registry.category("fields").add("favoriteButtonField", favoriteButtonField);
