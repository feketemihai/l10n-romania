# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine,self)._prepare_invoice_line(qty)
        if self.product_id.invoice_policy == 'delivery':
            res['account_id'] = self.company_id.property_stock_picking_receivable_account_id.id or res['account_id']
            #res['account_id'] = self.company_id.property_stock_picking_payable_account_id.id or res['account_id']
        return res