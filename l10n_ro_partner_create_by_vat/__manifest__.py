# -*- coding: utf-8 -*-
# Copyright  2015 Forest and Biomass Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Romania - Partner Create by VAT',
    'summary': 'Romania - Partner Create by VAT',

    'version': '10.0.1.0.0',
    'author': 'Forest and Biomass Romania, '
              'Odoo Community Association (OCA)',
    "website": "http://www.forbiom.eu",
    "category": "Localization",
    "depends": ['l10n_ro', 'base_vat'],
    "description": """
Partner create by VAT
---------------------
Fetches Partner data from openapi/mfinante or VIES

Pentru preluare date partener de pe OpenAPI.ro trebuie adaugata cheia in 'openapi_key' din parametrii sistemului
    """,

    'data': [
        'views/res_partner_view.xml',
    ],
    'installable': True,
    'license': 'AGPL-3',
    'application': False,
    'auto_install': False,
}
