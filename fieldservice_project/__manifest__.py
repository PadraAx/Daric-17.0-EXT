# Copyright (C) 2019 - TODAY, Patrick Wilson
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Field Service - Project",
    "summary": "Create field service orders from a project or project task",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "author": "TORAHOPER",
    'category': "Services/Field Service",
    "website": "https://torahoper.ir",
    "depends": ["fieldservice", "project"],
    "data": [
        "views/project_views.xml",
        "views/project_task_views.xml",
        "views/fsm_location_views.xml",
        "views/fsm_order_views.xml",
        "security/ir.model.access.csv",
        "views/fsm_team.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/fieldservice_project/static/src/scss/project_column.scss",
        ]
    },
    "installable": True,
}
