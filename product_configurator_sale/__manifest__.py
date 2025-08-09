# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Product Configurator Sale",
    "version": "17.0.1.0.0",
    "category": "Inventory/Product",
    "summary": "Product configuration interface modules for Sale",
    "author": "TORAHOPER",
    "license": "AGPL-3",
    "website": "https://torahoper.ir",
    "depends": ["sale_management", "product_configurator", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "data/menu_product.xml",
        "views/sale_view.xml",
    ],
    "demo": ["demo/res_partner_demo.xml"],
    "application": True,
    "installable": True,
    "auto_install": True,
    "development_status": "Beta",
    "maintainers": ["PCatinean"],
}
