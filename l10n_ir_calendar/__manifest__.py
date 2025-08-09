{
    "name": "Iran - Calendar",
    "version": "0.1",
    "countries": ["ir"],
    "category": "Localization/Iran",
    "description": "Jalali calendar, date and date-time widgets.",
    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    "depends": ["web"],
    "external_dependencies": {
        "python": ["khayyam"],
    },
    "data": [],
    "demo": [],
    "license": "LGPL-3",
    "installable": True,
    #'application': True,
    "auto_install": True,
    "module_type": "unofficial",
    "assets": {
        "web.assets_backend": [
            # the following "after" action should be before normal ones
            (
                "after",
                "web/static/src/search/utils/dates.js",
                "l10n_ir_calendar/static/src/search/utils/dates.js",
            ),
            # should be after the "after action
            "l10n_ir_calendar/static/src/**/*",
        ],
        "web._assets_core": [
            (
                "after",
                "web/static/src/core/l10n/dates.js",
                "l10n_ir_calendar/static/src/core/l10n/dates.js",
            ),
        ],
    },
}
