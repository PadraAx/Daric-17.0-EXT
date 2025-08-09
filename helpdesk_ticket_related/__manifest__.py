# Copyright 2024 Antoni Marroig(APSL-Nagarro)<amarroig@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Helpdesk Ticket Related",
    "summary": "Link tickets to each other",
    "version": "17.0.1.0.0",
    "category": "Services/Helpdesk",
    "website": "https://torahoper.ir",
    "author": "TORAHOPER",
    "maintainers": ["peluko00"],
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "depends": [
        "helpdesk_mgmt",
    ],
    "data": [
        "views/helpdesk_ticket_views.xml",
    ],
}
