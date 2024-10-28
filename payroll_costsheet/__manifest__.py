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
    'name': 'Payroll Costsheet Customization',
    'version': '17.0',
    'summary': 'payrol, sale, mrp',
    'description': """
        This module contains Payroll Costsheet Customization
        """,
    'category': 'payrol ...',
    'author': "Softrose,Mtloob",
    'company': 'Onsolutionc LLC.',
    'maintainer': 'Onesolutionc Development Team',
    'website': "https://www.onesolutionc.com",
    'depends': ['hr_payroll','hr_work_entry','hr_timesheet', 'project','planning'],
    'data': [
        'data/server_action.xml',
        'views/hr_work_entry_view.xml',
        'views/account_analytic_line_view.xml',
        'views/planning_slot_view.xml',
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
