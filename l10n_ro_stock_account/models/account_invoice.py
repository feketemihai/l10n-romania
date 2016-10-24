# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _prepare_invoice_line_from_po_line(self, line):
        data = super(AccountInvoice,self)._prepare_invoice_line_from_po_line(line)
        if line.product_id.purchase_method == 'receive':
            #data['account_id'] = line.company_id.property_stock_picking_receivable_account_id.id or data['account_id']
            data['account_id'] = line.company_id.property_stock_picking_payable_account_id.id or data['account_id']
        return data

