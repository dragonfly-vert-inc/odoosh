# -*- coding: utf-8 -*-
# Task ID: 1946175
{
    'name': "Dragon Fly - Vert:  Stock Modification",

    'summary': """
        Auto-fill destination location for Sales Order and Stock Picking""",

    'description': """
        Dragon Fly - Vert : Auto-fill destination location

        In order to know what products are at which job site, we are interpreting the 2-step delivery of a sales order as following:

        PICK = move from warehouse to job site (e.g. move wall from warehouse to job site)

        OUT = consume products at job site (e.g. install wall at job site)

        In order to reflect in the inventory reports which products are at which job sites, we will create sublocations of WH/Output and do the picking to the jobsite specific sub locations. This will give us a clear overview.

        The problem this creates is a lot of manual work and potential error when assigning the correct sub location in the detailed operations tab (stock.move.line).

        This dev will fix that issue by assigning the sub location once on the SO level. This will then automatically fill that location as destination location for all created stock move lines
    """,

    'author': "Odoo",
    'website': "http://www.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Custom Development',
    'version': '0.1',
    'sequence': 200,
    'license': 'OEEL-1',
    # any module necessary for this one to work correctly
    'depends': ['stock', 'sale','sale_stock'],

    # always loaded
    'data': [
        'views/sale_order_views.xml',
        'views/stock_picking_views.xml'
    ],

}
