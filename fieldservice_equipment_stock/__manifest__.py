# Copyright (C) 2020, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Stock Equipment",
    "summary": "Integrate stock operations with your field service equipments",
    "version": "17.0.1.0.0",
    'category': "Services/Field Service",
    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    "depends": [
        "fieldservice_stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/fsm_equipment.xml",
        "views/product_template.xml",
        "views/stock_picking_type.xml",
        "views/stock_lot.xml",
    ],
    "license": "AGPL-3",
    "development_status": "Beta",
    "maintainers": [
        "brian10048",
        "wolfhall",
        "max3903",
        "smangukiya",
    ],
}
