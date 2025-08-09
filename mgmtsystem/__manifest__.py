# Copyright (C) 2010 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Compliance/Management System",
    "version": "17.0.1.1.0",
    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    "license": "AGPL-3",
    "category": "Compliance/Management System",
    "depends": ["base"],
    "data": [
        "security/mgmtsystem_security.xml",
        "security/ir.model.access.csv",
        "views/menus.xml",
        "views/mgmtsystem_system.xml",
        "views/res_config.xml",
    ],
    "installable": True,
    "application": True,
}
