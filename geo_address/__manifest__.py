# -*- coding: utf-8 -*-
{
    "name": "Geo Address Management",
    "summary": "World’s most complete hierarchical geo-addressing and profiling system with full partner and entity integration",
    "description": """
This module offers the most advanced and extensible system for global geographic addressing, spatial profiling, and entity-level scoring.

Key Capabilities:
- Fully hierarchical location modeling: from country → region → city → building → unit → component → subcomponent
- Generation of globally unique 48-character location IDs and 60-character profile IDs
- Multi-profile versioning per entity with issuer and timestamp, supporting up to 99 profiles per object
- Attribute-based profiling with support for all data types (selection, boolean, integer, float, etc.)
- Universal UoM (Unit of Measure) compatibility with automatic conversion across metric and imperial systems
- Define scoring rules for any numeric attribute by creating as many weighted **value ranges** as needed
  e.g., width 0–10m = 5pts, 10–20m = 20pts, etc.
- Propagation and aggregation of attributes up and down the entity hierarchy
- Built-in UI-driven scientific calculation engine for real-time computation of derived attributes
- Fully dynamic structure: users can define, edit, or remove attribute types, scoring rules, components, and formulas
- Postal code rules per country, custom formats, and verification logic
- 3D positioning with lat/long/alt attributes for advanced spatial indexing

This platform acts as a complete **spatial, architectural, and legal profiling framework**, ideal for governments, real estate systems, infrastructure registries, and smart city platforms.
""",
    "version": "17.0.1.0.0",
    "category": "Localization",
    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    "license": "LGPL-3",
    "depends": ["base", "base_address_extended", "contacts", "mail", "uom", "web"],
    "data": [
        # ====================================================
        # SECURITY
        # ====================================================
        "security/security.xml",
        "security/ir.model.access.csv",
        # ====================================================
        # REGIONAL VIEWS
        # ====================================================
        "views/reg/res_country_views.xml",
        "views/reg/res_country_group_views.xml",
        "views/reg/res_country_state_views.xml",
        "views/reg/res_county_views.xml",
        "views/reg/res_city_views.xml",
        "views/reg/res_city_div_views.xml",
        "views/reg/res_rural_dist_views.xml",
        "views/reg/res_rural_dist_div_views.xml",
        "views/reg/postal_code_prefix_rule_views.xml",
        "views/reg/res_postal_code_prefix_views.xml",
        # ====================================================
        # INHERITED VIEWS
        # ====================================================
        "views/iht/res_partner_views.xml",
        # ====================================================
        # WIZARD VIEWS
        # ====================================================
        "wizard/address_image_wizard.xml",
        # ====================================================
        # ADDRESS VIEWS
        # ====================================================
        "views/res_address_views.xml",
        # ====================================================
        # ENTITY VIEWS
        # ====================================================
        "views/entities/bldg_building_views.xml",
        "views/entities/bldg_group_views.xml",
        "views/entities/bldg_floor_views.xml",
        "views/entities/bldg_group_type_views.xml",
        "views/entities/bldg_category_views.xml",
        "views/entities/bldg_building_physical_type_views.xml",
        "views/entities/bldg_floor_type_views.xml",
        "views/entities/bldg_unit_type_views.xml",
        "views/entities/bldg_unit_views.xml",
        # ====================================================
        # PROFILING VIEWS
        # ====================================================
        "views/profiles/bldg_prof_views.xml",
        "views/profiles/bldg_attr_views.xml",
        "views/profiles/bldg_scoring_rule_views.xml",
        # ====================================================
        # MENU ITEMS
        # ====================================================
        "views/menus.xml",
        # ====================================================
        # DATA FILES
        # ====================================================
        "data/res.country.state.csv",
        "data/res_country_data.xml",
        "data/res.county.csv",
        "data/res.city.csv",
        "data/res.city.div.csv",
        "data/res.rural.dist.csv",
        "data/bldg.category.csv",
        "data/bldg.group.type.csv",
        "data/bldg.building.physical.type.csv",
        "data/bldg.floor.type.csv",
        "data/bldg_unit_type_data.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "geo_address/static/src/js/postal_code_rules.js",
            "geo_address/static/src/js/copy_address_widget.js",
            "geo_address/static/src/css/postal_code_styles.css",
            "geo_address/static/src/css/copy_address.css",
            "static/src/xml/copy_address_template.xml",
        ]
    },
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
    "images": ["static/description/icon.png"],
    "installable": True,
    "application": True,
    "auto_install": False,
}
