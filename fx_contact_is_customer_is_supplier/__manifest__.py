{
    "name": "Customer and Vendor Management",
    "summary": "Distinguish between customers and vendors in partners",
    "description": """
        This module extends the res.partner model by adding two boolean fields: is_a_customer and is_a_vendor.
        It also adds domain filters to the partner field in sale and purchase order forms, allowing only customers or vendors to be selected, respectively.
    """,
    "version": "17.0.0.1.0",
    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    'category': 'Sales/CRM',
    "depends": ["contacts", "sale_management", "purchase"],
    "data": [
        "views/inherit_res_partner_view.xml",
        "views/inherit_sale_order_view.xml",
        "views/inherit_purchase_order_view.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": [
        "static/description/icon.png",
    ],
}
