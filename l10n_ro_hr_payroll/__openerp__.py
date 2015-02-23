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
===============================
This module deals with Romanian Payroll implementation.

Public Holidays
---------------
* depends on hr_public_holidays module

* Tag all employees with necessary tag.

* Define Public Leaves type and enter all leave dates in Public Holidays, enter
  the appropriate year, tag, leave type, Approve and Close.

* Closing the Public Holiday will automatically generate an allocation for all
  dates for all employees tagged and will create leave requests for all dates.

* TBD what happens with new employees (no holiday)


Wage History
------------
* Used to compute base for Sick Leaves and others as given by `ANAF <http://static.anaf.ro/static/10/Anaf/Declaratii_R/AplicatiiDec/structura_dunica_A304_2015_230115.pdf>`_


Meal Vouchers
-------------
* Set the value of the meal voucher in Company -> HR 

* Calculates the number of vouchers per employee 

* Meal voucher report


Company Payroll Taxes
---------------------
* Setup company taxes used in Payroll


Employee Contract
-----------------
* Advantages used as INPUT lines in Payroll calculation.

* Programmer or Handicap boolean are exceptions for paying Income Tax


Holidays
--------
* Sets Sick Leave Code

    """,
    'data': [
        # views
        #'views/report_meal_vouchers.xml',
        'views/hr_payroll.xml',
        'views/hr_contract.xml',
        'views/res_company.xml',
        'views/hr_holidays.xml',
        'views/hr_meal_vouchers.xml',
        'views/hr_wage_history.xml',
        'views/hr_public_holidays.xml',
        # workflows
        'workflows/hr_public_holidays_workflow.xml',
        # data
        'data/hr.wage.history.csv',
        'data/hr.employee.category.csv',
        'data/hr.holidays.status.csv',
        'data/hr.holidays.public.csv',
        'data/hr.holidays.public.line.csv',
        'data/hr.contribution.register.csv',
        # reports
        'report/hr_meal_vouchers.xml',
        'report/report_meal_vouchers_template.xml',
        # model access
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
