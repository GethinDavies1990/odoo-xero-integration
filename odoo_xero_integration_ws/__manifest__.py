# -*- coding: utf-8 -*-
{

    'name': "Odoo Xero Connector",

    'summary': """
        Xero (Customers, Products, Invoices, Purchase Orders) Integration with ODOO.""",

    'description': """
        Synchronization of ODOO with Xero.
        Once data created in Xero, will be reflected in ODOO by justone click.
    """,

    'author': "WoadSoft",
    'website': "https://woadsoft.com/odoo-integration-with-xero/",
    'category': 'Tools',
    'version': '1.0',
    'depends': ['base', 'product', 'account', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'external_dependencies': {
        'python': [],
    },
    'price': 110,
    'currency': 'EUR',
    'license': 'OPL-1',
    'images':["images/banner.gif"]
}
