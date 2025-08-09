# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Helpdesk Project",
    "summary": "Add the option to select project in the tickets.",
    "version": "17.0.1.0.1",
    "license": "AGPL-3",
    'category': 'Services/Helpdesk',
    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    "depends": ["helpdesk_mgmt", "project"],
    "data": [
        "views/helpdesk_ticket_view.xml",
        "views/helpdesk_ticket_team_view.xml",
        "views/project_view.xml",
        "views/project_task_view.xml",
    ],
    "development_status": "Production/Stable",
    "auto_install": True,
    "application": True,
}
