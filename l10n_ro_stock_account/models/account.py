# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Fekete Mihai <mihai.fekete@forbiom.eu>
#    Copyright (C) 2014 FOREST AND BIOMASS SERVICES ROMANIA SA
#    (http://www.forbiom.eu).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, _


class AccountAccount(models.Model):
    _inherit = "account.account"

    @api.multi
    @api.constrains('internal_type', 'reconcile')
    def _check_reconcile(self):
        accounts = self.env['account.account']
        for account in self:
            if account != self.company_id.property_stock_picking_payable_account_id and \
                    account != self.company_id.property_stock_picking_receivable_account_id:
                accounts |= account

        super(AccountAccount, accounts)._check_reconcile()


class account_move_line(models.Model):
    _inherit = "account.move.line"

    stock_picking_id = fields.Many2one('stock.picking', string='Stock Picking',
                                       help='This account move line has been generated by this stock picking')
    stock_move_id = fields.Many2one('stock.move', string='Stock Move',
                                    help='This account move line has been generated by this stock move')
    stock_inventory_id = fields.Many2one('stock.inventory', string='Stock Inventory',
                                         help='This account move line has been generated by this inventory')
