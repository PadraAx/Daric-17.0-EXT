# -*- coding: utf-8 -*-
# Part of Daric. See LICENSE file for full copyright and licensing details.

{
    "name" : "Sales Commission",
    "version" : "17.0.0.0",
    'category' : "Sales/Commissions",
    "summary" : "Calculate commission for sales orders, invoices, and payments based on product margin, category, or partner in Odoo.",
    "description": """
        This module calculates sales commission on invoices, sales orders, and payments. It includes commission based on product category, product margin, partner, and more.
        The system calculates commissions for internal and external sales partners, sales agents, and users. It also supports commission calculation on product, margin, sales orders, invoices, and payments.
        Features:
        - Sales commission for users, partners, and agents
        - Commission based on product category, margin, or partner
        - Sales commission on sales orders, invoices, and payments
        - Supports commissions for internal and external sales agents
        - Calculate commission based on margin, product, or sales amount
        - Reports for commission calculation and status
        """,
    "author" : "TORAHOPER",
    "website" : "https://torahoper.ir",
    "price": 60,
    "currency": 'EUR',
    "depends" : ['base', 'sale', 'sale_management', 'sale_stock', 'sale_margin'],
    "data" :[
        'security/sales_commission_security.xml',
        'security/ir.model.access.csv',
        'account/account_invoice_view.xml',
        'commission_view.xml',
        'base/res/res_partner_view.xml',
        'sale/sale_config_settings.xml',
        'sale/sale_view.xml',
        'report/commission_report.xml',
        'report/sale_inv_comm_template.xml'
    ],
    "application" : True,
    "auto_install": False,
    "installable": True,
    "live_test_url":'https://youtu.be/4BlRGFqPiO8',
    "images":['static/description/Banner.gif'],
    'license': 'OPL-1',
}
