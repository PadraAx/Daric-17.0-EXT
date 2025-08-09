{
    "name": "HR Time off Extra",
    "version": "17.1",
    "license": 'LGPL-3',
    "category": "Human Resources",
    "summary": "Add Holiday Extra",
    "author": "TORAHOPER",
    'website': "https://daric-saas.ir",
    "depends": [
        "hr_holidays", "employee_ext", "hr_payroll_holidays" ,
    ],
    "data": [
        # security
        "security/ir.model.access.csv",
        "security/hr_holidays_security.xml",

        # wizard

        # views
        "views/hr_employee_public_views.xml",
        "views/hr_employee_views.xml",
        "views/hr_leave_allocation_views.xml",
        "views/hr_leave_type_views.xml",
        "views/hr_leave_views.xml",
        "views/resource_calendar_leaves_views.xml",
        "views/resource_views.xml",
        "views/resource_calendar_views.xml",
        "views/resource_calendar_attendance_views.xml",

        # report

        # Menu
        "views/hr_holidays_views.xml",

        # data
        "data/types_of_time_off.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'hr_holidays_ext/static/src/js/calendar_year_renderer.js',
            'hr_holidays_ext/static/src/css/calendar.css',
            'hr_holidays_ext/static/src/dashboard/time_off_card.xml',
        ],
    },
    "installable": True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
