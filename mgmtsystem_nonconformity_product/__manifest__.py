# Copyright 2019 Marcelo Frare (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# Copyright 2019 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)

{
    "name": "Management System - Nonconformity Product",
    "summary": "Bridge module between Product and Management System.",
    "version": "17.0.1.0.0",
    "development_status": "Beta",
    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    "license": "AGPL-3",
    "category": "Compliance/Management System",
    "depends": ["product", "mgmtsystem_nonconformity"],
    "data": ["views/mgmtsystem_nonconformity_views.xml"],
    "installable": True,
}
