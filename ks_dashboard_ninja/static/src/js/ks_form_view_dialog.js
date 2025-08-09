/** @odoo-module **/

import { FormViewDialog } from "@web/views/view_dialogs/form_view_dialog";
import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";
import { onMounted } from "@odoo/owl";

patch(FormViewDialog.prototype, {
    setup() {
        onMounted(this._mounted)
        super.setup()
    },
    _mounted() {
        if (this.props.context) {
            const ksFormView = this.props.context.ks_form_view ? this.props.context.ks_form_view : false;
            if (ksFormView == true) {
                $('body').addClass('ks_dn_create_chart')
            }
        }

    },

});
patch(FormController.prototype, {
    beforeExecuteActionButton(clickParams) {
        if (this.props.context) {
            const ksFormView = this.props.context.ks_form_view ? this.props.context.ks_form_view : false;
            if (ksFormView == true && clickParams.special == 'cancel') {
                $('body').removeClass('ks_dn_create_chart')
            }
        }
        return super.beforeExecuteActionButton(...arguments)
    },
});

