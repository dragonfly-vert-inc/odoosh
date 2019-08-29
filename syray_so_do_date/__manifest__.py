# -*- coding: utf-8 -*-
{
    'name': "SO-Line Date and Priority",

    'summary': """
        * New date field, priority and Action button column in sales order line""",

    'description': """
        * A custom date field for every sales order line as Delivery Date
        * A custom priority selector field with three values (Low, Medium, High) with related color (Green, Yellow, Red)
        * New Column for Action button
        * New View MTO and Update button
    """,

    'author': "Syncoria",
    'website': "http://www.syncoria.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock', 'sale', 'sale_stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/future_date_asset.xml',
        'views/so_line_view.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}