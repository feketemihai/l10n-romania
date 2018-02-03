# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014 Deltatech All Rights Reserved
#                    Dorin Hongu <dhongu(@)gmail(.)com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################




import time
from datetime import datetime
from odoo import api, models
from odoo.tools import formatLang
from amount_to_text_ro import *

class ReportInvoiceWithPaymentsPrint(models.AbstractModel):
    _name = 'report.account.report_invoice_with_payments'
    _template = 'account.report_invoice_with_payments'

    @api.model
    def get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name(self._template)
        return  {
            'doc_ids': docids,
            'doc_model': report.model,
            'data': data,
            'time': time,
            'docs': self.env[report.model].browse(docids),
            'convert': self._convert,
            'with_discount': self._with_discount,
            'formatLang': self._formatLang
        }

    def _formatLang(self, value, *args):
        return formatLang(self.env, value, *args)


    def _convert(self, amount):
        amt_ro = amount_to_text_ro(amount)
        return amt_ro


    def _with_discount(self, invoice):
        res = False
        for line in invoice.invoice_line_ids:
            if line.discount <> 0.0:
                res = True
        return res



class ReportInvoicePrint(models.AbstractModel):
    _name = 'report.account.report_invoice'
    _template = 'account.report_invoice'


    @api.model
    def get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name(self._template)
        return  {
            'doc_ids': docids,
            'doc_model': report.model,
            'data': data,
            'time': time,
            'docs': self.env[report.model].browse(docids),
            'convert': self._convert,
            'with_discount': self._with_discount,
            'formatLang': self._formatLang
        }






    def _formatLang(self, value, *args):
        return formatLang(self.env, value, *args)


    def _convert(self, amount):
        amt_ro = amount_to_text_ro(amount)
        return amt_ro


    def _with_discount(self, invoice):
        res = False
        for line in invoice.invoice_line_ids:
            if line.discount <> 0.0:
                res = True
        return res





