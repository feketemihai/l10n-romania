# -*- coding: utf-8 -*-
# ©  2015-2018 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import formatLang
import time

class PosInvoiceReport(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_invoice'


    @api.model
    def get_report_values(self, docids, data=None):
        values = super(PosInvoiceReport, self).get_report_values(docids, data)
        values.update({
            'data': data,
            'time': time,
            'convert': self._convert,
            'with_discount': self._with_discount,
            'formatLang': self._formatLang,
            'get_pickings': self._get_pickings,
        })
        return values


    def _get_pickings(self, invoice):
        pickings = self.env['stock.picking']
        return pickings


    def _formatLang(self, value, *args):
        return formatLang(self.env, value, *args)


    def _convert(self, amount):
        amt_ro = amount
        # amt_ro = amount_to_text_ro(amount)
        return amt_ro


    def _with_discount(self, invoice):
        res = False
        for line in invoice.invoice_line_ids:
            if line.discount != 0.0:
                res = True
        return res