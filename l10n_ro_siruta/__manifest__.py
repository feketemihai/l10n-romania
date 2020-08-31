# -*- coding: utf-8 -*-
# ©  2015 Forest and Biomass Services Romania
# See README.rst file on addons root folder for license details

{
    'name': 'Romania - Siruta',
    'summary': 'Romania - Siruta',
    'version': '13.0.1.0.0',
    'category': 'Localization',
    "description": """
Creates models for storing zones, communes.
Links between country - zone - state - commune - cities.
Partner address fields extended with zone and commune.
City field from partners is related to city_id.name.
Fields are added in partner and partner contact forms.

""",
    'author':
        'Terrabit'
        'Forest and Biomass Services Romania, '
              'Odoo Community Association (OCA)',
    'website': 'https://www.forbiom.eu',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': ['contacts','l10n_ro_city'],

    "data": [
        'views/partner_view.xml',
        'views/siruta_view.xml',
        'views/assets.xml',
        'security/ir.model.access.csv',

        #datele sunt incarcate doar la instalare prin post_init_hook
        #'data/res.country.zone.csv',
        #'data/res.country.state.csv',
        #'data/res.country.commune.csv',

    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "maintainers": ["dhongu"],
}
