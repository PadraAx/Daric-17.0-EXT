/** @odoo-module */
import { registry } from "@web/core/registry";
import { formView } from "@web/views/form/form_view";
import { FormController } from "@web/views/form/form_controller";
import { ConfirmationDialog } from "@web/core/dialog/confirmation_dialog";
import { useService } from "@web/core/utils/hooks";

class BldgProfFormController extends FormController {
    setup() {
        super.setup();
        this.dialog = useService("dialog");
    }

    async save() {
        try {
            await super.save();
        } catch (error) {
            if (!error.data?.message?.includes("[skip_profile_lock_confirm]")) {
                throw error;
            }
            await new Promise((resolve, reject) => {
                this.dialog.add(ConfirmationDialog, {
                    title: this.env._t("Confirm new profile"),
                    body: error.data.message,
                    confirm: async () => {
                        const model = this.props.resModel;
                        const resId = this.model.root.resId;
                        const dirty = this.model.root.changes;
                        const ctx = { skip_profile_lock_confirm: true };

                        try {
                            if (resId) {
                                await this.model.orm.write(
                                    model,
                                    [resId],
                                    dirty,
                                    { context: ctx }
                                );
                            } else {
                                const values = { ...this.model.root.data, ...dirty };
                                await this.model.orm.create(
                                    model,
                                    [values],
                                    { context: ctx }
                                );
                            }
                            await this.model.load();
                            resolve();
                        } catch (e) {
                            reject(e);
                        }
                    },
                    cancel: () => reject(error),
                });
            });
        }
    }
}

registry.category("views").add("bldg_prof_form", {
    ...formView,
    Controller: BldgProfFormController,
});