
{
    'name': 'Hide Chatter',
    'version': '17.0.1.0.0',
    'category': 'System Administration/Users Access Management',
    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    'summary': 'Disable the chatter of specific models',
    'description': "Hide Chatter ",
    
    'depends': ['web','employee_ext','contract_ext','hr_payroll'],
    'data': [
        'views/view_employee_form_hide_chatter.xml',
        'views/view_hr_payslip_form_hide_chatter.xml',
        'views/hr_contract_view_form_hide_chatter.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    "application": True,
}
