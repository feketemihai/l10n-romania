# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Romanian  Intrastat Declaration",
    "version": "1.0",
    "category": "Reporting",
    "description": """
Generates Intrastat XML report for declaration
Based on invoices.
New report for invoice
    """,
    "author": "Dorin Hongu",
    "depends": [
        # 'report_intrastat',
        "product",
        "sale",
        "account",
        "l10n_ro",
    ],
    "data": [
        "data/country_data.xml",
        # 'data/report.intrastat.code.csv',
        "data/transaction.codes.xml",
        "data/transport.modes.xml",
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/l10n_ro_intrastat_view.xml",
        "views/product_view.xml",
        "views/res_country_view.xml",
        "views/account_intrastat_code_view.xml",
        "wizard/l10n_ro_intrastat_xml_view.xml",
        # 'views/report_invoice.xml'
    ],
    "installable": True,
}
