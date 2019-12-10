# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Syncoria PLM Upgrade Manufacturing Orders',
    'summary': 'Syncoria PLM Upgrade Manufacturing Orders',
    'website': 'http://www.ergo-ventures.com',
    'version': '1.0',
    'author': 'Ergo Ventures Ltd.',
    'description': """
    """,
    'category': 'Custom Development',
    'depends': ['mto_chain', 'mrp_plm'],
    'data': [
        'views/mrp_bom.xml',
        'views/mrp_eco.xml',
        'views/wizard.xml'
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
