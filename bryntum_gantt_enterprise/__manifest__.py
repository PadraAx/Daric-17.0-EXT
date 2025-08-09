# -*- coding: utf-8 -*-
{
    'name': "Gantt View PRO",

    'summary': """
    Manage and visualise your projects with the fastest Gantt chart on the web.
    """,

    'description': """
    Bryntum Gantt chart is the most powerful Gantt component available. It has a massive set of features that will cover all your project management needs.
    """,

    'author': "TORAHOPER",
    'website': "https://torahoper.ir",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Performance',
    'version': '2.1.1',
    'license' : 'Other proprietary',

    'support' : 'support@daric-saas.ir',
    'live_test_url': 'https://daric-saas.ir',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'project','hr'],
    'images' : ['images/banner.png', 'images/main_screenshot.png','images/reschedule.gif'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/project_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'application': True,
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/bryntum_gantt_enterprise/static/src/js/bryntum_gantt_controller.js',
            '/bryntum_gantt_enterprise/static/src/js/bryntum_arch_parser.js',
            '/bryntum_gantt_enterprise/static/src/**/*.xml',
            '/bryntum_gantt_enterprise/static/src/js/bryntum_gantt_renderer.js',
            '/bryntum_gantt_enterprise/static/src/js/view.js',
            '/bryntum_gantt_enterprise/static/src/css/main.css'
        ]
    },
}
