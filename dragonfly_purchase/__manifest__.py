# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Dragon Fly PO Approval Flow',
    'summary': 'Dragon Fly PO Approval Flow',
    'sequence': 100,
    'license': 'OEEL-1',
    'website': 'https://www.odoo.com/page/purchase',
    'version': '1.1',
    'author': 'Odoo Inc',
    'description': """
PO Approval Flow
================
This module will add four step approval on RFQ
- Manager Approval
- VP Approval
- VP Finance Approval
- CEO Approval

Depending on the total value of the RFQ, the approval flow will be different and different users might need to be notified.

*The matrix below shows what needs to happen in each of the possible use cases:

------------------------------------------------------------------------------------------
PO total amount |    Manager    |   Controller   |     VP     |  VP Finance  |    CEO    |
------------------------------------------------------------------------------------------
<500            |    CC         |     CC         |      /     |   Approval   |    /      |
>= 500 < 2K     |    Approval   |     CC         |      /     |   Approval   |    /      |
>=2K < 10K      |    Approval   |     CC         |  Approval  |   Approval   |    /      |
>=10K           |    Approval   |     CC         |  Approval  |   Approval   |  Approval |
------------------------------------------------------------------------------------------



    """,
    'category': 'Custom Development',
    'depends': ['purchase', 'hr'],
    'data': [
        # security
        'security/ir.model.access.csv',

        # views
        'views/purchase_view.xml',
        'views/res_config_settings_view.xml',

        # data
        'data/data.xml',

    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
