# -*- coding: utf-8 -*-
# ©  2014 Forest and Biomass Services Romania
# See README.rst file on addons root folder for license details

{
    'name': 'Romania - Account Period Close',
    'version': '10.0.1.0.0',
    'author': 'FOREST AND BIOMASS SERVICES ROMANIA',
    'website': 'http://www.forbiom.eu',
    'category': 'Localization',
    'description': """
    Account Period Close - The module allows to close periodically accounts
    based on templates defines.
    Usefull for Income / Expense / VAT closing at the end of every month""",
    'depends': ['base', 'account'],
    'data': [
            'security/ir.model.access.csv',
            'security/account_security.xml',
            'views/account_period_close_view.xml',
            'wizard/account_period_closing.xml',
    ],
    'installable': True,
}
