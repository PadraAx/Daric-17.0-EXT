# Copyright 2013 Camptocamp SA - Guewen Baconnier
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Reservation",
    "summary": "Stock reservations on products",
    "version": "17.0.1.0.0",
    "author": "TORAHOPER",
    "category": "Inventory/Warehouse",
    "license": "AGPL-3",
    "complexity": "normal",
    "website": "https://torahoper.ir",
    "depends": ["stock"],
    "data": [
        "view/stock_reserve.xml",
        "view/product.xml",
        "data/stock_data.xml",
        "security/ir.model.access.csv",
        "data/cron.xml",
    ],
    "auto_install": False,
    "installable": True,
}
