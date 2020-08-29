# Copyright (C) 2020 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.tools import float_compare, float_round, float_is_zero


class StockMove(models.Model):
    _inherit = "stock.move"

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
        valued_types += [ 'in_notice', 'out_notice', 'in_inventory', 'out_inventory']
        return valued_types

    # in functie de tipul de miscare se va pune in context valued_type pentru a se obtine contrul dorit
    def _get_accounting_data_for_valuation(self):
        valued_type = False
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
        #
        self = self.with_context(standard=True)
        return super(StockMove, self)._account_entry_move(qty, description, svl_id, cost)
