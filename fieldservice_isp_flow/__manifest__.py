# Copyright (C) 2021 - Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Flow for ISP",
    "summary": "Field Service workflow for Internet Service Providers",
    "version": "17.0.1.0.0",
    'category': "Services/Field Service",
    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    "depends": [
        "fieldservice",
    ],
    "data": [
        "data/fsm_stage.xml",
        "views/fsm_order.xml",
    ],
    "application": False,
    "license": "AGPL-3",
    "development_status": "Beta",
    "maintainers": ["osi-scampbell"],
}
