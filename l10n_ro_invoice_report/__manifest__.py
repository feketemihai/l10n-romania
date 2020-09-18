# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Romania - Invoice Report",
    "version": "13.0.1.0.0",
    "author": "Dorin Hongu," "Odoo Community Association (OCA)",
    "website": "",
    "description": """

Romania - Invoice Report layout
------------------------------------------

Functionalitati
 - factura contine: pretul fara tva, valoare si valoare tva
 - La factura au fost adugate campurile delegat si mijloc de transport
 - la partener se poate adauga un text aditinonal care apara pe facura
 - tiparire plata / incasare / dispozitie de plata


 pip3 install --force-reinstall num2words==0.5.9


 https://static.anaf.ro/static/10/Anaf/legislatie/Cod_fiscal_norme_31072017.htm#A330


    """,
    "category": "Generic Modules",
    "depends": ["base", "account", "l10n_ro_config", "deltatech_watermark"],
    "data": [
        "views/invoice_report.xml",
        "views/voucher_report.xml",
        "views/payment_report.xml",
        # 'views/account_invoice_view.xml',
        "views/account_voucher_report.xml",
        "views/account_bank_statement_view.xml",
        "views/statement_report.xml",
        # 'views/res_partner_view.xml',
    ],
    "active": False,
    "installable": True,
}
