# Copyright (C) 2019, Patrick Wilson
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - CRM",
    "version": "17.0.1.1.0",
    "summary": "Create Field Service orders from the CRM",
    'category': "Services/Field Service",
    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    "depends": ["fieldservice", "crm"],
    "data": [
        "views/crm_lead.xml",
        "views/fsm_location.xml",
        "views/fsm_order.xml",
        "security/ir.model.access.csv",
    ],
    "license": "AGPL-3",
    "development_status": "Beta",
    "maintainers": ["patrickrwilson"],
    "installable": True,
}
