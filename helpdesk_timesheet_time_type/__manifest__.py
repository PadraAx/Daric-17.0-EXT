# Copyright 2025 Lansana Barry Sow(APSL-Nagarro)<lbarry@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Helpdesk Timesheet Time Type",
    "version": "17.0.1.0.0",
    "category": "Services/Helpdesk",
    "website": "https://torahoper.ir",
    "author": "TORAHOPER",
    "maintainers": ["lbarry-apsl"],
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "depends": [
        "helpdesk_mgmt_timesheet",
        "hr_timesheet_time_type",
    ],
    "data": [
        "views/helpdesk_ticket_view.xml",
    ],
}
