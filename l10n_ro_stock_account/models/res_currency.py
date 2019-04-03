# -*- coding: utf-8 -*-
# ©  2008-2019 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import api, fields, models, _


class Currency(models.Model):
    _inherit = "res.currency"

    @api.multi
    def is_zero(self, amount):
        if self.env.context.get('force_account_move_with_zero', False):
            return False
        return super(Currency, self).is_zero(amount)
