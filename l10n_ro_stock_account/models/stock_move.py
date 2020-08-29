# Copyright (C) 2020 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.tools import float_compare, float_round, float_is_zero


class StockMove(models.Model):
    _inherit = "stock.move"



    @api.model
    def _get_valued_types(self):
        valued_types = super(StockMove, self)._get_valued_types()
        valued_types += [
            'reception',  # receptie de la furnizor fara avaiz
            'reception_return',         # retur la o receptie de la funizor fara aviz
            'delivery',  # livrare din stoc fara aviz
            #   'delivery_return',          # storno livrare
            'reception_notice',
            #    'reception_notice_return',
             'delivery_notice',
            #   'delivery_notice_return',
            'plus_inventory',
            'minus_inventory'
        ]
        return valued_types

    # nu se mai face in mod automat evaluarea la intrare in stoc
    def _create_in_svl(self, forced_quantity=None):
        if self.env.context.get('standard'):
            svl = super(StockMove, self)._create_in_svl(forced_quantity)
        else:
            svl = self.env['stock.valuation.layer']
        return svl

    # nu se mai face in mod automat evaluarea la iserirea din stoc
    def _create_out_svl(self, forced_quantity=None):
        if self.env.context.get('standard'):
            svl = super(StockMove, self)._create_out_svl(forced_quantity)
        else:
            svl = self.env['stock.valuation.layer']
        return svl

    # evaluare la receptie - in mod normal nu se
    def _is_reception(self):
        """ Este receptie in stoc fara aviz"""
        return not self.picking_id.notice and self.location_id.usage == 'supplier' and self._is_in()

    def _create_reception_svl(self, forced_quantity=None):
        print('SVL reception')
        svl = self.with_context(standard=True, valued_type='reception')._create_in_svl(forced_quantity)
        return svl

    def _is_reception_return(self):
        """ Este un retur la o receptie in stoc fara aviz"""
        return not self.picking_id.notice and self.location_dest_id.usage == 'supplier' and self._is_out()

    def _create_reception_return_svl(self, forced_quantity=None):
        print('SVL reception return')
        svl = self.with_context(standard=True, valued_type='reception_return')._create_out_svl(forced_quantity)
        return svl

    def _is_reception_notice(self):
        """ Este receptie in stoc cu aviz"""
        return self.picking_id.notice and self._is_in()

    def _create_reception_notice_svl(self, forced_quantity=None):
        print('SVL reception notice')
        svl = self.with_context(standard=True, valued_type='reception_notice')._create_in_svl(forced_quantity)
        return svl

    def _is_reception_notice_return(self):
        """ Este receptie in stoc cu aviz"""
        return self.picking_id.notice and self._is_out()

    def _create_reception_notice_return_svl(self, forced_quantity=None):
        forced_quantity = -forced_quantity
        svl = self.with_context(standard=True, valued_type='reception_notice_return')._create_in_svl(forced_quantity)
        return svl

    def _is_delivery(self):
        """ Este livrare din stoc fara aviz"""
        return not self.picking_id.notice and self.location_dest_id.usage == 'customer' and self._is_out()

    def _create_delivery_svl(self, forced_quantity=None):
        svl = self.with_context(standard=True,valued_type='delivery')._create_out_svl(forced_quantity)
        return svl

    def _is_delivery_return(self):
        """ Este retur la o livrare din stoc fara aviz"""
        return not self.picking_id.notice and self.location_id.usage == 'customer' and self._is_in()

    def _create_delivery_return_svl(self, forced_quantity=None):
        svl = self.with_context(standard=True,valued_type='delivery_return')._create_in_svl(forced_quantity)
        return svl

    def _is_delivery_notice(self):
        """ Este livrare cu aviz"""
        return self.picking_id.notice and self.location_dest_id.usage == 'customer' and self._is_out()

    def _create_delivery_notice_svl(self, forced_quantity=None):
        svl = self.with_context(standard=True,valued_type='delivery_notice')._create_out_svl(forced_quantity)
        return svl

    def _is_delivery_notice_return(self):
        """ Este livrare cu aviz"""
        return self.picking_id.notice and self.location_id.usage == 'customer' and self._is_in()

    def _create_delivery_notice_return(self, forced_quantity=None):
        svl = self.with_context(standard=True,valued_type='delivery_notice')._create_out_svl(forced_quantity)
        return svl

    def _is_plus_inventory(self):
        self.ensure_one()
        return self.location_id.usage == 'inventory' and self.location_dest_id.usage == 'internal'

    def _create_plus_inventory_svl(self, forced_quantity=None):
        svl = self.with_context(standard=True,valued_type='plus_inventory_')._create_in_svl(forced_quantity)
        return svl

    def _is_minus_inventory(self):
        self.ensure_one()
        return self.location_id.usage == 'internal' and self.location_dest_id.usage == 'inventory'

    def _create_minus_inventory_svl(self, forced_quantity=None):
        svl = self.with_context(standard=True,valued_type='minus_inventory_')._create_out_svl(forced_quantity)
        return svl

    def _prepare_common_svl_vals(self):
        vals = super(StockMove, self)._prepare_common_svl_vals()
        valued_type = self.env.context.get('valued_type')
        if valued_type:
            vals['valued_type'] = valued_type
        return vals

    # in functie de tipul de miscare se va pune in context valued_type pentru a se obtine contul dorit
    def _get_accounting_data_for_valuation(self):
        valued_type = self.env.context.get('valued_type')
        if not valued_type:
            if self._is_reception():
                valued_type = 'reception'
            elif self._is_reception_notice():
                valued_type = 'reception_notice'
            elif self._is_plus_inventory():
                valued_type = 'plus_inventory'
            elif self._is_in():
                valued_type = 'in'

            if self._is_delivery():
                valued_type = 'delivery'
            elif self._is_delivery_notice():
                valued_type = 'delivery_notice'
            elif self._is_out_inventory():
                valued_type = 'minus_inventory'
            elif self._is_out():
                valued_type = 'out'

            self = self.with_context(valued_type=valued_type)
        return super(StockMove, self)._get_accounting_data_for_valuation()

    def _account_entry_move(self, qty, description, svl_id, cost):
        """ Accounting Valuation Entries """
        self.ensure_one()
        if self.product_id.type != 'product':
            # no stock valuation for consumable products
            return False
        if self.restrict_partner_id:
            # if the move isn't owned by the company, we don't make any valuation
            return False

        location_from = self.location_id
        location_to = self.location_dest_id
        company_from = self._is_out() and self.mapped('move_line_ids.location_id.company_id') or False
        company_to = self._is_in() and self.mapped('move_line_ids.location_dest_id.company_id') or False

        if self._is_delivery_notice():
            # inregistrare vanzare
            sale_cost = self._get_sale_amount()
            move = self.with_context(force_company=company_from.id, valued_type='invoice_out_notice')
            journal_id, acc_src, acc_dest, acc_valuation = move._get_accounting_data_for_valuation()
            move._create_account_move_line(acc_valuation, acc_dest, journal_id, qty, description, svl_id, cost)

        self = self.with_context(standard=True)
        res = super(StockMove, self)._account_entry_move(qty, description, svl_id, cost)

        return res

    def _get_sale_amount(self):
        valuation_amount = 0
        sale_line = self.sale_line_id
        if sale_line:
            price_invoice = sale_line.price_subtotal / sale_line.product_uom_qty
            valuation_amount = price_invoice * abs(self.product_qty)
            company = self.location_id.company_id
            valuation_amount = sale_line.order_id.currency_id._convert(
                valuation_amount, company.currency_id, company, self.date
            )
        return valuation_amount

    def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id,
                                  cost):
        # nu mai trebuie generate notele contabile de la cont de stoc la cont de stoc
        if credit_account_id == debit_account_id:
            return
        return super(StockMove, self)._create_account_move_line(
            credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost)
