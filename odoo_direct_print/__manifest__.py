{
    "name": "Direct Print",
    "version": "17.0.1.2",
    "category": "System Administration/Base",
    "summary": """Print any report or shipping label or barcode label directly to any local (usb, wifi, bluetooth, network) printer without downloading PDF""",
    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    'live_test_url': 'https://appdemo.skyerp.net',
    "license": "OPL-1",
    "price": 49.99,
    "currency": "EUR",
    "depends": [
        # Odoo
        'base',
        'web',
    ],
    "data": [
        # Views
        'views/ir_actions_report.xml',
    ],
    "assets": {
        "web.assets_backend": [
            "/odoo_direct_print/static/lib/print.min.js",
            "/odoo_direct_print/static/lib/print.min.css",
            "/odoo_direct_print/static/src/js/browser_print_dialog.js",
        ],
        "web.assets_qweb": [],
    },
    "images": ['static/description/banner.gif'],
    "installable": True,
    "application": True,
}
