# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "POS Product Modifier",
    "author": "Softhealer Technologies",
    "license": "OPL-1",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Point of Sale",
    "summary": "POS Product Toppings Topping Group With Topping Products Add Multiple Toppings In Cart Product Global Toppings In Cart Product Print Toppings On Receipt Mass Update Product Mass Product Update Pizza Modifier Food Modifier Product Update POS Topping POS Toppings POS Product Topping Point Of Sale Product Topping Point Of Sale Product Toppings Point Of Sale Topping Point Of Sale Toppings Odoo",
    "description": """This module provides topping products for your resturant. You can create a topping group and add topping product in it. When you add to cart toppings group all relevant topping products automatically added in cart. We provide functionality to add global topping in POS cart.""",
    "version": "0.0.2",
    "depends": ["point_of_sale","pos_restaurant"],
    "application": True,
    "data": [ 
        'security/ir.model.access.csv',
        'views/pos_category_views.xml',
        'views/product_product_views.xml',
        'views/res_config_settings_views.xml',
        'views/sh_product_toppings.xml',
        'views/sh_topping_group.xml',
     ],
     'assets': { 'point_of_sale._assets_pos': [
            'sh_pos_product_toppings/static/src/overrides/**/*',
            'sh_pos_product_toppings/static/src/app/**/*',
            ],
        },
     
    "images": ["static/description/background.png", ],
    "auto_install": False,
    "installable": True,
    "price": 35,
    "currency": "EUR"
}
