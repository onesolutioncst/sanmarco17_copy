# -*- coding: utf-8 -*-
{
    'name': "Custom Pagebreak in Quotation Report",
    'summary': """
        Modification in Quotation Report.""",
    'description': """
        Modification in Quotation Report by adding pagebreak at sale order line level.
    """,
    'author': "Onesolutionc",
    'company': 'Onesolutionc',
    'website': "http://www.onesolutionc.com",
    'category': 'sale',
    'version': '17.0',
    'depends': ['sale', 'sale_management', 'web'],
    'data': [
        'views/sale_order_views.xml',
        'report/sale_order_report_layout.xml',
    ],
    'images': [
        'static/description/banner.jpg',
    ],
    'installable': True,
    'license': 'OPL-1',
}
