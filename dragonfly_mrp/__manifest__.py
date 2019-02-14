# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Dragon Fly MRP Enhancement',
    'summary': 'Dragon Fly MRP Enhancement',
    'sequence': 100,
    'license': 'OEEL-1',
    'website': 'https://www.odoo.com/page/purchase',
    'version': '1.1',
    'author': 'Odoo Inc',
    'description': """
MRP Enhancement
===============

* [1938284]
    -  This will add a button ('Documents') on the work order process screen that will create a new tab in the browser with the attachment screen of the product
       that is selected on the related manufacturing order.


    """,
    'category': 'Custom Development',
    'depends': ['mrp_workorder', 'mrp_plm'],
    'data': [
        # security
        # views
        'views/mrp_workorder_view.xml',
        # data

    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
