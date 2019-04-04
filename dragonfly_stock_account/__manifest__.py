# -*- coding: utf-8 -*-
{
    'name': "Dragon Fly - Vert:  Custom automated inventory valuation",

    'summary': """
        Custom automated inventory valuation""",

    'description': """
        Dragon Fly - Vert : Custom automated inventory valuation

    """,

    'author': "Odoo",
    'website': "http://www.odoo.com",

    'category': 'Custom Development',
    'version': '0.1',
    'sequence': 200,
    'license': 'OEEL-1',
    'depends': ['stock_account'],

    'data': [
        'views/stock_picking_views.xml'
    ],

}
