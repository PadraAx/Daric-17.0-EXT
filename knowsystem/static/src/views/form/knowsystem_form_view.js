/** @odoo-module **/

import { registry } from "@web/core/registry";
import { formView } from "@web/views/form/form_view";
import { KnowSystemFormController } from "./knowsystem_form_controller";


export const KnowSystemFormView = { ...formView, Controller: KnowSystemFormController };

registry.category("views").add("knowsystem_form", KnowSystemFormView);
