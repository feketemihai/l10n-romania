# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Fekete Mihai <mihai.fekete@forbiom.eu>
#              Dorin Hongu <dhongu@gmail.com>
#    Copyright (C) 2014 FOREST AND BIOMASS SERVICES ROMANIA SA
#    (http://www.forbiom.eu).
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
    "name": "Romania - Stock Accounting",
    "version": "1.0",
    "author": "FOREST AND BIOMASS SERVICES ROMANIA, Terrabit",
    "website": "http://www.forbiom.eu",
    "category": "Warehouse",
    "depends": ['stock_account', 'account', 'l10n_ro_config', 'l10n_ro_stock', 'purchase'],

    'data': [
        'views/stock_view.xml',
        'views/stock_account_view.xml',
        'views/product_view.xml',
        'views/account_invoice_view.xml',
        'report/daily_stock_report_view.xml',
        'report/daily_stock_report_template.xml'
    ],
    'installable': True,
    'active': False,
}
