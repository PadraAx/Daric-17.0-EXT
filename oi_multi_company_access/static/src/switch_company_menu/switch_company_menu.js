/** @odoo-module **/

import { SwitchCompanyItem } from "@web/webclient/switch_company_menu/switch_company_menu";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";
import { useService } from "@web/core/utils/hooks";

patch(SwitchCompanyItem.prototype, {

    setup() {
		super.setup();
        this.orm = useService("orm");
    },

    get multi_company_access() {
        return session.multi_company_access;
    },

    async logIntoCompany() {		
		if (this.isCompanyAllowed && this.multi_company_access) {
			await this.orm.silent.write("res.users", [session.uid], {
				company_id: this.props.company.id,
			});
		}
		super.logIntoCompany();		
	}

});