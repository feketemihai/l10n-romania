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
    "name": "Romania - Account Reports",
    "version": "1.0",
    "author": "FOREST AND BIOMASS SERVICES ROMANIA	",
    "website": "http://www.forbiom.eu",

    "category": "Romania Adaptation",
    "depends": [
        'account',
        'report',
        'account_vat_on_payment',
        'l10n_ro_invoice_line_not_deductible',
        'l10n_ro_invoice_report',
        'l10n_ro_config',
    ],

    "description": """
Romania  - Accounting Reports
------------------------------------------


    """,

    'data': ['data/report_paperformat.xml',
             'views/report_trialbalance.xml',
             'views/report_trialbalance_html.xml',
             'views/report_sale_journal.xml',
             'views/report_account_bank_statement.xml',
             'views/report_sale_journal_html.xml',
             'views/report_purchase_journal.xml',
             'views/report_purchase_journal_html.xml',
             'views/layouts.xml',
             'account_report.xml',
             'wizard/account_report_account_balance_view.xml',
             'wizard/account_report_sale_purchase_journal_view.xml',],
    'installable': True,
    'auto_install': False,
}
