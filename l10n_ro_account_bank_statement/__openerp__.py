# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Fekete Mihai <mihai.fekete@forbiom.eu>
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
    "name": "Romania - Bank Statement Operations",
    "version": "1.0",
    "author": "FOREST AND BIOMASS SERVICES ROMANIA	",
    "website": "http://www.forbiom.eu",
    "category": "Romania Adaptation",
    "depends": ['account', 'l10n_ro_config', 'account_statement_operation_multicompany', 'l10n_ro_currency_reevaluation'],
    "description": """
Romania  - Bank Statement Operations
------------------------------------------


    """,

    'data': ['bank_statement_import.xml', ],
    'installable': True,
    'auto_install': False,
}
