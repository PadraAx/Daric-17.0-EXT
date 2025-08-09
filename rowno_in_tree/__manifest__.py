{
    "name": "Row Number",
    "version": "17.0.0.0.0",
    "summary": "Show row number.",
    "author": "TORAHOPER",
    'category': 'System Administration/Backend UI', 
    "website": "https://torahoper.ir",
    "depends": ["web_grid","web"],
    "data": [],
    "assets": {
        "web.assets_backend": [
            # "rowno_in_tree/static/src/views/list/list_render.xml",
            # "rowno_in_tree/static/src/js/o2many_row_no.js",
            "rowno_in_tree/static/src/js/list_render.xml",
            "rowno_in_tree/static/src/js/row_no_list_renderer.js",
        ]
    },
    "installable": True,
    "application": False,
    "auto_install": True,
}
