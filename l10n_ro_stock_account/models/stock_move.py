# Copyright (C) 2020 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.tools import float_compare, float_round, float_is_zero


class StockMove(models.Model):
    _inherit = "stock.move"

    picking_type_code = fields.Selection(
        related="picking_id.picking_type_code",
        readonly=True,
        help="Taken from stock_picking_type.code",
    )


    def _is_in(self):
        if self.env.context.get('standard'):
            return super(StockMove, self)._is_in()
        if self.picking_id.notice:
            return False
        elif self.location_id.usage == 'inventory' and self.location_dest_id.usage == 'internal':
            return False
        else:
            return super(StockMove, self)._is_in()

    def _is_out(self):
        if self.env.context.get('standard'):
            return super(StockMove, self)._is_out()
        if self.picking_id.notice:
            return False
        elif self.location_id.usage == 'internal' and self.location_dest_id.usage == 'inventory':
            return False
        else:
            return super(StockMove, self)._is_out()

    def _is_in_notice(self):
        """ Este receptie in stoc cu aviz"""
        return self.picking_id.notice and self.with_context(standard=True)._is_in()

    def _create_in_notice_svl(self, forced_quantity=None):
        svl = self.with_context(standard=True)._create_in_svl(forced_quantity)
        return svl

    def _is_out_notice(self):
        """ Este livrare cu aviz"""
        return self.picking_id.notice and self.with_context(standard=True)._is_out()

    def _create_out_notice_svl(self, forced_quantity=None):
        svl = self.with_context(standard=True)._create_out_svl(forced_quantity)
        return svl

    def _is_in_inventory(self):
        self.ensure_one()
        return self.location_id.usage == 'inventory' and self.location_dest_id.usage == 'internal'

    def _create_in_inventory_svl(self, forced_quantity=None):
        svl = self.with_context(standard=True)._create_in_svl(forced_quantity)
        return svl

    def _is_out_inventory(self):
        self.ensure_one()
        return self.location_id.usage == 'internal' and self.location_dest_id.usage == 'inventory'

    def _create_out_inventory_svl(self, forced_quantity=None):
        svl = self.with_context(standard=True)._create_out_svl(forced_quantity)
        return svl

    @api.model
    def _get_valued_types(self):
        valued_types = super(StockMove, self)._get_valued_types()
        valued_types += ['in_notice', 'out_notice', 'in_inventory', 'out_inventory']
        return valued_types

    # in functie de tipul de miscare se va pune in context valued_type pentru a se obtine contrul dorit
    def _get_accounting_data_for_valuation(self):
        valued_type = self.env.context.get('valued_type')
        if not valued_type:
            if self._is_in_notice():
                valued_type = 'in_notice'
            elif self._is_in_inventory():
                valued_type = 'in_inventory'
            elif self._is_in():
                valued_type = 'in'

            if self._is_out_notice():
                valued_type = 'out_notice'
            elif self._is_out_inventory():
                valued_type = 'out_inventory'
            elif self._is_out():
                valued_type = 'out'

            self = self.with_context(valued_type=valued_type)
        return super(StockMove, self)._get_accounting_data_for_valuation()

    def _account_entry_move(self, qty, description, svl_id, cost):
        self.ensure_one()

        location_from = self.location_id
        location_to = self.location_dest_id

        if self._is_out_notice():
            # inregistrare vanzare
            sale_cost = self._get_sale_amount()
            company_from = self.mapped('move_line_ids.location_id.company_id') or False
            move = self.with_context(force_company=company_from.id, valued_type='invoice_out_notice')
            journal_id, acc_src, acc_dest, acc_valuation = move._get_accounting_data_for_valuation()

            move._create_account_move_line(acc_valuation, acc_dest, journal_id, qty, description, svl_id, sale_cost)

        self = self.with_context(standard=True)
        res = super(StockMove, self)._account_entry_move(qty, description, svl_id, cost)

        return res

    def _get_sale_amount(self):

        sale_line = self.sale_line_id
        price_invoice = sale_line.price_subtotal / sale_line.product_uom_qty
        valuation_amount = price_invoice * abs(self.product_qty)
        company = self.location_id.company_id
        valuation_amount = sale_line.order_id.currency_id._convert(
            valuation_amount, company.currency_id, company, self.date
        )
        return valuation_amount

    def _action_done(self, cancel_backorder=False):
        move_in_notice = self.env['stock.move']
        for move in self:
            if move._is_in_notice():
                move_in_notice |= move.with_context(standard=True)

        move_in_notice.product_price_update_before_done()

        res = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)

        return res
