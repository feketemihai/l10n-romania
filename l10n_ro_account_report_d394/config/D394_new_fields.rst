.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

=============================
Romania - D394 Account Report
=============================

Version 3 - starting from 01.07.2016

`Companies <https://github.com/feketemihai/l10n-romania/tree/new_d394/l10n_ro_account_report_d394/models/res_company.py>`_.

Fields added:

* ANAF Crosschecking - option to allow ANAF crosschecking.
* Is Fiscal representative - boolean field to know if the company is fiscal
  represented by another partner.
* Fiscal representative - Partner representing the company.

`Country states <https://github.com/feketemihai/l10n-romania/tree/new_d394/l10n_ro_account_report_d394/models/res_country_states.py>`_.

Fields added:

* Order Code - Country state order.

The field in completed at module install/update from data file.

`Sequences <https://github.com/feketemihai/l10n-romania/tree/new_d394/l10n_ro_account_report_d394/models/ir_sequence.py>`_.

Fields added:

* Sequence Type - Selection field to choose the type of invoicing:

  * Normal invoicing
  * Autoinvoicing emmited by supplier (Customer Invoice)
  * Autoinvoicing emitted by company (Supplier Invoice)
* Serie First Number - First number of sequence at the beggining of
  fiscalyear - available in internal decision about ordering.
* Serie Last Number - Last number of sequence at the beggining of
  fiscalyear - available in internal decision about ordering.
* Partner - In autoinvoicing, the field in storing the partner associated
  with this sequence.
