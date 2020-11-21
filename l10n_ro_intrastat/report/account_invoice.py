# ©  2008-2020 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

import time

from odoo.osv import osv
from odoo.report import report_sxw

from odoo.addons.l10n_ro_invoice_report.report.account_invoice import report_invoice_print

# from odoo.addons.l10n_ro_invoice_report.report.amount_to_text_ro  import *


class ReportInvoiceIntrastat(osv.AbstractModel):
    _name = "report.report_intrastat.report_intrastatinvoice"
    _inherit = "report.abstract_report"
    _template = "report_intrastat.report_intrastatinvoice"
    _wrapped_report_class = report_invoice_print
