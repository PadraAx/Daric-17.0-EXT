# -*- coding: utf-8 -*-

# Part of Daric. See LICENSE file for full copyright and licensing details.
{
    'name': "Salesperson Customer Access",
    'version': '10.2.2',
    'license': 'Other proprietary',
    'summary': """Enable salespeople to manage only their assigned customers, sales orders, and invoices.""",
    'description': """
Daric Salesperson Access Control
================================

This module enables controlled access for salespeople, allowing them to view and manage only their own customers, sales orders, and invoices. It helps streamline operations and ensures data security within your sales team.

Key Features:
- Salespeople can access only their assigned customers on quotations, sales orders, and invoices.
- Managers can assign multiple salespeople to a single customer.
- Provides flexibility to configure customer access for sales teams.
- Includes access rules to enforce salesperson-specific visibility.

Additional Features:
- Multi-salesperson assignment for customers.
- Restriction and control for salesperson views.
- Easy configuration and setup.

For more details, visit: https://daric-saas.ir
""",
    'author': "TORAHOPER",
    'website': "https://torahoper.ir",
    'support': 'support@daric-saas.ir',
    'live_test_url': 'https://daric-saas.ir/demo',
    'images': ['static/description/main_img.jpg'],
    'category': 'Sales/Sellers Management',
    'depends': ['sale_management'],
    'data': [
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
        'views/account_invoice_view.xml',
        'security/security.xml',
        'security/record_rule.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
