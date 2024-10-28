# -*- coding: utf-8 -*-
###################################################################################
#    A part of OneSolutionc Apps
#
#    Onesolutionc Technologies Pvt. Ltd.
#    Copyright (C) 2024-TODAY Onesolutionc Technologies (<https://www.onesolutionc.com>).
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
    'name': 'Project Analytic Balance',
    'version': '17.0',
    'summary': 'project accounting',
    'description': """
        This module get project balance from entries
        """,
    'category': 'project...',
    'author': "Onesolutionc ",
    'company': 'Onsolutionc LLC.',
    'maintainer': 'Onesolutionc Development Team',
    'website': "https://www.onesolutionc.com",
    'depends': ['project'],
    'data': [
        'views/project_project_views.xml'
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}