# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Fieldservice Availability",
    "version": "17.0.1.0.1",
    "summary": "Provides models for defining blackout days, stress days, "
    "and delivery time ranges for FSM availability management.",
    'category': "Services/Field Service",
    "website": "https://torahoper.ir",
    "author": "TORAHOPER",
    "maintainers": ["ppyczko"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["fieldservice_route"],
    "data": [
        "security/ir.model.access.csv",
        "views/fsm_blackout_day_templates.xml",
        "views/fsm_delivery_time_range_templates.xml",
        "views/fsm_stress_day_templates.xml",
        "views/menu.xml",
    ],
}
