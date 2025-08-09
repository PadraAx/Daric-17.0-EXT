{
    "name": "Metrics",
    "summary": """
        Corporate Dashboard.
    """,

    "category": "Performance/Metrics",
    'author': "TORAHOPER",
    'website': "https://torahoper.ir",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["mail", "resource"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_metric.xml",
        "views/menu.xml",
        "views/ir_metric.xml",
        
    ],
    "installable": True,
    'application': True,
    "auto_install": False,
    "images": ["images/screen.png"],
    "external_dependencies": {"python": ["prometheus_client"]},
}
