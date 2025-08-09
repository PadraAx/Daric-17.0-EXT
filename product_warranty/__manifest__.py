# Copyright (C) 2009-2011  Akretion, Emmanuel Samyn
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Product Warranty",
    "version": "17.0.1.0.0",
    "category": "Inventory/Product",
    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    "license": "AGPL-3",
    "depends": ["sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_company_views.xml",
        "views/product_supplierinfo_views.xml",
        "views/product_template_views.xml",
        "views/return_instructions_views.xml",
    ],
    "demo": ["demo/product_warranty.xml", "demo/res_company.xml"],
    "images": ["images/product_warranty.png"],
    "development_status": "Production/Stable",
    "maintainers": ["osi-scampbell", "max3903"],
}
