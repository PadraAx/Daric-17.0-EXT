{
    "name": "Product Allowed on User",

    'version': "17.0",

    'category': "Inventory/Product",

    "summary": "This app will Allowed selected Products for particular user.",

    'author': "TORAHOPER",

    'website': "https://torahoper.ir",

    "depends": ['product'],

    "data": [
        "security/security.xml",
        "views/res_users_views.xml",
    ],

    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}
