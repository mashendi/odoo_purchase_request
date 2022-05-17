# -*- coding: utf-8 -*-
{
    'name': "Purchase Request",

    'summary': """
        Purchase Request Module""",

    'description': """
        Purchase Request
    """,

    'author': "Shendi",
    'website': "https://www.yds-int.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_request.xml',
        'views/purchase_order.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
