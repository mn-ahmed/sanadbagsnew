# -*- coding: utf-8 -*-


{
    'name': 'Merge PO RFQs',
    'version': '13.0.0.0',
    'summary': """This module merge the Purchase order rfq's.""",
    'description': """
    This module merge the Purchase order rfq's
    """,
    'author': 'Viltco',
    'website': 'http://www.viltco.com',
    'category': 'purchase',
    'depends': ['purchase'],
    'data': [
        'data/server.xml',
        'views/purchase_order_merge_view.xml',
    ],
    'installable': True,
    'application': False,
}
