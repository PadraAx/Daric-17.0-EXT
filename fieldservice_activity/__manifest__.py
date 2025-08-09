# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Field Service Activity",
    "summary": """Field Service Activities are a set of actions
     that need to be performed on a service order""",
    "version": "17.0.1.1.0",
    'category': "Services/Field Service",
    "license": "AGPL-3",
    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    "depends": ["fieldservice"],
    "data": [
        "views/fsm_order.xml",
        "views/fsm_template.xml",
        "security/ir.model.access.csv",
    ],
    "development_status": "Beta",
    "maintainers": ["max3903", "osi-scampbell"],
}
