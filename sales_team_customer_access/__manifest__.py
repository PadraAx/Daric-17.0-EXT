# -*- coding: utf-8 -*-

# Part of Daric. See LICENSE file for full copyright and licensing details.
{
    'name': "Sales Team Customer Access",
    'version': '9.1.2',
    'license': 'Other proprietary',
    'summary': """Limited Customers / Contacts for Sales Team Members""",
    'description': """
        This module allows Salesperson(s) to access only their own customers/contacts in sales orders, quotations, and invoices.
        Features:
        - Salesperson can access only customers where they are assigned as Salesperson
        - Option to assign multiple Salespersons to a single customer
        - Restrict access to customers, vendors, and sales orders based on salesperson assignment
        - Provides a clear view of only their customers for Salespersons in sales orders and invoices
        - Managers can assign multiple Salespersons to a customer
        - Set custom permissions for Salespersons on customer, vendor, sales orders, invoices, and more
        - Multiple Salespersons can be assigned to a single customer for better collaboration
        - Includes record rules to ensure data access is strictly controlled
    """,
    'author': "TORAHOPER",
    'website': "https://torahoper.ir",
    'support': 'support@daric-saas.ir',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/sales_team_customer_access/118',
    'images': ['static/description/image.png'],
    'category' : 'Sales/Sellers Management',
    'depends': ['sales_person_customer_access'],
    'data':[
        'views/res_partner_view.xml',
        'security/record_rule.xml',
    ],
    'installable' : True,
    'application' : True,
    'auto_install' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
