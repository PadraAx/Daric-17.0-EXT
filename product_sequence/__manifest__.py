# Copyright 2004 Tiny SPRL
# Copyright 2016 Sodexis
# Copyright 2018 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Sequence",
    "version": "17.0.1.0.0",
    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    "license": "AGPL-3",
    "category": "Inventory/Product",
    "depends": ["product"],
    "data": [
        "data/product_sequence.xml",
        "views/product_category.xml",
        "views/res_config_settings_views.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "installable": True,
}
