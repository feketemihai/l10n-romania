# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Account Vat On Payment',
    'version' : '1.0',
    'summary': '',
    'sequence': 4,
    'description': """

    """,
    'category': 'Accounting',
    'website': 'https://www.odoo.com/page/accounting',
    'depends' : ['account_tax_cash_basis'],
    'data': [
        'data/data.xml'
    ],
    'installable': True,
    'auto_install': False,
}
