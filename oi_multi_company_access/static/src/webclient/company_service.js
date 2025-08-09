/** @odoo-module **/

import { companyService } from "@web/webclient/company_service";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";
import { cookie } from "@web/core/browser/cookie";

const CIDS_HASH_SEPARATOR = "-";

function parseCompanyIds(cids, separator = ",") {
    if (typeof cids === "string") {
        return cids.split(separator).map(Number);
    } else if (typeof cids === "number") {
        return [cids];
    }
    return [];
}

function computeActiveCompanyIds(cids) {
    const { user_companies } = session;
    let activeCompanyIds = cids || [];
    const availableCompaniesFromSession = user_companies.allowed_companies;
    const notAllowedCompanies = activeCompanyIds.filter(
        (id) => !(id in availableCompaniesFromSession)
    );

    if (!activeCompanyIds.length || notAllowedCompanies.length) {
        activeCompanyIds = [user_companies.current_company];
    }
    return activeCompanyIds;
}

function getCompanyIdsFromBrowser(hash) {
    let cids;
    if ("cids" in hash) {
        // backward compatibility s.t. old urls (still using "," as separator) keep working
        // deprecated as of 17.0
        let separator = CIDS_HASH_SEPARATOR;
        if (typeof hash.cids === "string" && !hash.cids.includes(CIDS_HASH_SEPARATOR)) {
            separator = ",";
        }
        cids = parseCompanyIds(hash.cids, separator);
    } else if (cookie.get("cids")) {
        cids = parseCompanyIds(cookie.get("cids"));
    }
    return cids || [];
}


patch(companyService, {
    start(env, { user, router, action }) {
        let companyIds = false;
        if (session.multi_company_access) {
            const activeCompanyIds = computeActiveCompanyIds(
                getCompanyIdsFromBrowser(router.current.hash)
            );
            const {current_company} = session.user_companies;
            if (activeCompanyIds.length > 1 || !activeCompanyIds.includes(current_company)) {
                companyIds = [current_company];
            }        
        }
        const res = super.start(env, { user, router, action });
        if (companyIds) {
            res.setCompanies(companyIds, false);
        }

        return res;
    }
});