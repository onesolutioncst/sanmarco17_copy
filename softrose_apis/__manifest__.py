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
    'name': 'Softrose Mobile Integration Apis',
    'version': '17.0.1.0.0',
    'summary': 'apis',
    'description': """
        This module contains Softrose mobile apis
        """,
    'category': 'website, apis ...',
    'author': "Softrose,Mtloob, Ezz",
    'company': 'Softrose Technologies Pvt. Ltd',
    'maintainer': 'Softrose Development Team',
    'website': "https://www.Softrose.com",
    'depends': ['sale_margin','rest_api_integration','sale','base_geolocalize','stock','account','crm_salesperson_planner','hr_expense'],
    'data': [
        'views/res_partner_view.xml',
        'views/res_user_view.xml',
        'views/stock_location_view.xml',
        'views/crm_salesperson_planner_visit_view.xml',
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}