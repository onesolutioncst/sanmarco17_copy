# -*- encoding: utf-8 -*-
{
    "name": "ODOO REST API Integration",
    "version": "17.0",
    "category": "base",
    'author': 'OneSolutionc',
    "description": """
        There are URIs available:
        
        /api/auth                   POST    - Login in Odoo and set cookies
        
        /api/<model>                GET     - Read all (with optional domain, fields, offset, limit, order)
        /api/<model>/<id>           GET     - Read one (with optional fields)
        /api/<model>                POST    - Create one
        /api/<model>/<id>           PUT     - Update one
        /api/<model>/<id>           DELETE  - Delete one
        /api/<model>/<id>/<method>  PUT     - Call method (with optional parameters)

    """,
    "depends": ['base','web'],
    "data": [
        'views/res_config_settings_views.xml',
        'views/res_users_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
