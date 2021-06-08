# -*- coding: utf-8 -*-
{
    'name': "Purchase Payment Reserve",

    'summary': """
        Purchase Payment Reserve""",

    'description': """
        Purchase Payment Reserve
    """,

    'author': "Viltco",
    'website': "http://www.viltco.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'purchase',
    'version': '14.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'security/security.xml',
        'views/views.xml',
        # 'views/report_payment_voucher.xml',
        # 'views/report.xml',
        'wizards/advance_payment_wizard.xml',
    ],

}
