# Copyright (C) 2010 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Management System - Review",
    "version": "17.0.1.1.0",
    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    "license": "AGPL-3",
    "category": "Compliance/Management System",
    "depends": ["mgmtsystem_nonconformity", "mgmtsystem_survey"],
    "data": [
        "security/ir.model.access.csv",
        "security/mgmtsystem_review_security.xml",
        "data/ir_sequence.xml",
        "views/mgmtsystem_review.xml",
        "views/res_users.xml",
        "report/review.xml",
        "report/report.xml",
    ],
    "installable": True,
}
