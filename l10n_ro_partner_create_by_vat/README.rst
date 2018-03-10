.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

===============================
Romania - Partner Create by VAT
===============================

This module allows you to create the partners (companies) based on their
VAT number. It will complete the name, address of the partner from
different sources.

Sources from where the datas are fetched:

ANAF
https://webservicesp.anaf.ro/PlatitorTvaRest/api/v1/

OpenAPI
http://openapi.ro

Installation
============

To install this module, you need to:

* clone the branch 11.0 of the repository https://github.com/OCA/l10n-romania
* add the path to this repository in your configuration (addons-path)
* update the module list
* search for "Romania - Partner Create by VAT" in your addons
* install the module

Usage
=====

Put the VAT number in the partner's form and save the new record

* If it'a a romanian company, the first source used is the ANAF, if an error is raised, the OpenAPI source is used.
* If it's not a romanian company, will use the datas from VIES Webservice if they are available.

Note:

* OpenAPI service is not always up to date with all the modifications from Ministry of Finance.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/177/11.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/l10n-romania/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Fekete Mihai <feketemihai@gmail.com>
* Dorin Hongu <dhongu@gmail.com>
* Adrian Vasile <adrian.vasile@gmail.com>

Do not contact contributors directly about support or help with technical issues.

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
