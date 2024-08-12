# -*- coding: utf-8 -*-
###################################################################################
#    A part of OneSolutionc Apps
#
#    Onesolutionc Technologies Pvt. Ltd.
#    Copyright (C) 2022-TODAY Onesolutionc Technologies (<https://www.onesolutionc.com>).
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
{
    'name': 'Costsheet Customization',
    'version': '17.0',
    'summary': 'sale, mrp',
    'description': """
        This module contains Costsheet from sale order (mrp order)
        """,
    'category': 'sale, mrp, project ...',
    'author': "Softrose,Mtloob",
    'company': 'Onsolutionc LLC.',
    'maintainer': 'Onesolutionc Development Team',
    'website': "https://www.onesolutionc.com",
    'depends': ['sale','mrp_account','purchase_requisition', 'fleet'],
    'data': [
        'data/server_action.xml',
        'security/delivery_security.xml',
        'security/ir.model.access.csv',
        'wizard/manufacture_agreement_views.xml',
        'views/mrp_production_view.xml',
        'views/sale_order_view.xml',
        'wizard/mrp_suborders_view.xml',
        'views/product_template_view.xml',
        'views/purchase_requisition_view.xml',
        # 'views/fleet_vehicle_view.xml',
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}