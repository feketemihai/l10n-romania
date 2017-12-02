# -*- coding: utf-8 -*-
# ©  2015 Forest and Biomass Services Romania
# See README.rst file on addons root folder for license details

{
    'name': 'Romania - Siruta',
    'summary': 'Romania - Siruta',
    'version': '10.0.1.0.0',
    'category': 'Localization',
    "description": """
Creates models for storing zones, communes.
Links between country - zone - state - commune - cities.
Partner address fields extended with zone and commune.
City field from partners is related to city_id.name.
Fields are added in partner and partner contact forms.

""",
    'author': 'Forest and Biomass Services Romania, '
              'Odoo Community Association (OCA)',
    'website': 'https://www.forbiom.eu',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': ["base", "sales_team"],

    "data": [
        'views/partner_view.xml',
        'views/siruta_view.xml',
        'views/assets.xml',
        'security/ir.model.access.csv',
        'data/l10n_ro/res.country.state.csv',
        'data/res.country.zone.csv',
        'data/res.country.state.csv',

        #
        # 'data/res_country_state.xml',

        # Load big data
        'data/res.country.commune.csv',
        'data/res.country.city.csv',
        'data/res_partner.yml',
    ],
    'images': ['static/description/customer.png',
               'static/description/address.png']
}
