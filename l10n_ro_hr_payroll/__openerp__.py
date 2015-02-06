# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Adrian Vasile <adrian.vasile@gmail.com>
#    Copyright (C) 2014 Adrian Vasile
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": "Romania - Payroll",
    "version": "1.0",
    "author": "Adrian Vasile",
    "website": "http://opennet.ro",
    "category": "Localization/Payroll",
    "depends": [
        'hr_holidays',
        'hr_public_holidays',
        'hr_payroll',
        'l10n_ro_hr',
    ],
    "description": """
    Romanian Payroll implementation
    -------------------------------
    1. Public Holidays
    Tag all employees with necessary tag.
    Define Public Leaves type and enter all leave dates in Public Holidays,
    enter the appropriate year, tag, leave type, Approve and Close.
    Closing the Public Holiday will automatically generate an allocation for
    all dates for all employees tagged and will create leave requests for all
    dates.
    """,
    'data': [
        'views/hr_payroll.xml',
        'views/hr_contract.xml',
        'views/res_company.xml',
        'views/hr_public_holidays.xml',
        'views/hr_wage_history.xml',
        'hr_public_holidays_workflow.xml',
#        'security/ir.model.access.csv',
    ],
    'installable': True,
}
