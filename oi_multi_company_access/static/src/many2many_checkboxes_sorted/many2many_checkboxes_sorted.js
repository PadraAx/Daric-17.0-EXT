/** @odoo-module **/

import {Many2ManyCheckboxesField, many2ManyCheckboxesField} from "@web/views/fields/many2many_checkboxes/many2many_checkboxes_field";
import { registry } from "@web/core/registry";

export class Many2ManyCheckboxesSortedField extends Many2ManyCheckboxesField {

    get items() {
        const result = super.items;
        result.sort((a,b) => a[1] < b[1] ? -1 : 1);
        return result;
    }

}

export const many2ManyCheckboxesSortedField = {
    ...many2ManyCheckboxesField,
    component: Many2ManyCheckboxesSortedField
}

registry.category("fields").add("many2many_checkboxes_sorted", many2ManyCheckboxesSortedField);