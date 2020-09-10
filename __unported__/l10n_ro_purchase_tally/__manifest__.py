# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2018 Terrabit Solutions. All rights reserved.
#    @author Dorin Hongu/Dan Stoica
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": "Purchase Tally",
    "version": "0.1",
    "author": "Terrabit",
    "website": "https://terrabit.ro",
    "depends": ["purchase", "l10n_ro_stock_picking_report", "deltatech_contact"],
    "data": [
        "views/stock_picking_report.xml",
        "wizard/tally_wizard.xml",
        "data/ir_sequence.xml",
        "data/report_format.xml",
    ],
    "description": """

Borderou achizitii persoane fizice
---------------------------------- 
  - Tiparire borderou achizitie din picking
    """,
    "category": "Generic Modules",
    "active": False,
    "installable": True,
}
