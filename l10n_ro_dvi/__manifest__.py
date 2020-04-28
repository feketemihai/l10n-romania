# -*- coding: utf-8 -*-
# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
{
    "name": "Romania - DVI",
    "version": "1.0",
    "author": "Terrabit",
    "website": "http://www.terrabit.ro",
    "category": "Warehouse",
    "depends": [
        'stock_account',
        'account',
        'l10n_ro_config',
        'l10n_ro_stock',
        'purchase_stock',
        'stock_landed_costs'
    ],

    'data': [
        'views/account_invoice_view.xml',
        'views/stock_landed_cost_view.xml',
        'wizard/account_dvi_view.xml'
    ],
    'installable': True,
    'active': False,
}
