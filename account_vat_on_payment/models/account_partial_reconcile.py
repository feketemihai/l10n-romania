# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class AccountPartialReconcileCashBasis(models.Model):
    _inherit = 'account.partial.reconcile'

    def _get_tax_cash_basis_lines(self, value_before_reconciliation):
        line_to_create, move_date = super(AccountPartialReconcileCashBasis, self)._get_tax_cash_basis_lines(
            value_before_reconciliation)
        if len(line_to_create) >= 4:
            line_to_create.pop(0)
            line_to_create.pop(0)
        return line_to_create, move_date
