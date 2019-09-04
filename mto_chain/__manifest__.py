# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Syncoria MTO Chain',
    'summary': 'Syncoria Make to Order Chain',
    'website': 'http://www.ergo-ventures.com',
    'version': '1.0',
    'author': 'Ergo Ventures Ltd.',
    'description': """
    """,
    'category': 'Custom Development',
    'depends': ['mrp','stock','sale','purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/mto_chain_view.xml',
        'views/sale_order.xml',
        'views/procurement_linking_wizard.xml',
        'views/mrp_production.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
