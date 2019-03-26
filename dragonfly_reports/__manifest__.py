# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Dragon Fly Reports Customization',
    'summary': 'Dragon Fly Reports Customization',
    'sequence': 100,
    'license': 'OEEL-1',
    'website': 'https://www.odoo.com/page/purchase',
    'version': '1.0',
    'author': 'Odoo Inc',
    'description': """
Reports Customization
=====================
The company address block at the top of the page to only show on the first page
For all Reports
    """,
    'category': 'Custom Development',
    'depends': ['web'],
    'data': [
        # reports
        'report/purchase_report.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
