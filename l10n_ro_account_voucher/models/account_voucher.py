# -*- coding: utf-8 -*-
# ©  2017 Terrabit
# See README.rst file on addons root folder for license details

from odoo import fields, models, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def first_move_line_get(self, move_id, company_currency, current_currency):
        move_line = super(AccountVoucher, self).first_move_line_get(move_id, company_currency, current_currency)
        if self.pay_now == 'pay_now' and self.amount > 0:
            move_line_411 = dict(move_line)
            move_line_411['account_id'] = self.partner_id.property_account_receivable_id.id \
                if self.voucher_type == 'sale' else self.partner_id.property_account_payable_id.id
            self.env['account.move.line'].create(move_line_411)
            move_line_411['debit'], move_line_411['credit'] = move_line_411['credit'], move_line_411['debit']
            self.env['account.move.line'].create(move_line_411)

        return move_line
