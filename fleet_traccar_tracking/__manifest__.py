# -*- coding: utf-8 -*-
#################################################################################
# Author      : Daric (<https://daric-saas.ir>)
# Copyright   : 2017-Present Daric
# License     : Other proprietary
# Website     : <https://daric-saas.ir>
#################################################################################

{
    "name": "Fleet Tracking",
    "summary": "Manage and track fleet movements with Daric.",
    "version": "17.1",
    "description": """
        This module allows users to handle tracking data and generate reports in Daric efficiently.
        It manages journeys, routes, and events for Traccar-integrated vehicles.
        
        Features:
        - Seamless integration of Traccar with Daric
        - Monitor vehicle movements and travel history
        - Generate detailed tracking reports
    """,    
    "author": "TORAHOPER",
    "maintainer": "Daric",
    "license": "Other proprietary",
    "website": "https://torahoper.ir",
    "images": ["images/fleet_traccar_tracking.png"],
    "category": "Human Resources/Fleet",
    "depends": ["base", "fleet"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/ir_cron_data.xml",
        "wizard/raise_message.xml",
        "wizard/wizard_traccar_device_summary.xml",
        "wizard/wizard_traccar_fetch_trips.xml",
        "wizard/wizard_traccar_fetch_routes.xml",
        "wizard/wizard_traccar_device_location.xml",
        "views/traccar_config_settings_views.xml",
        "views/fleet_vehicle_views.xml",
        "views/fleet_traccar_vehicle_views.xml",
        "views/traccar_trip_details_views.xml",
        "views/traccar_route_details_views.xml",
        "views/traccar_event_details_views.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "/fleet_traccar_tracking/static/src/js/*.js",
            "/fleet_traccar_tracking/static/src/css/*.css",
            "/fleet_traccar_tracking/static/src/xml/*.xml"
        ]
    },
    "installable": True,
    "application": True,
    "price": 150,
    "currency": "EUR",
    "pre_init_hook": "pre_init_check"
}
