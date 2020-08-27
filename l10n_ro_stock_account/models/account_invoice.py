# -*- coding: utf-8 -*-
# ©  2008-2018 Fekete Mihai <mihai.fekete@forbiom.eu>
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError
from odoo.tools.float_utils import float_compare, float_is_zero


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    def _stock_account_prepare_anglo_saxon_in_lines_vals(self):
        # inainte de a genera liniile de diferenta de pret

        account_id = self.company_id.property_stock_picking_payable_account_id
        get_param = self.env['ir.config_parameter'].sudo().get_param
        diff_limit = float(get_param('stock_account.diff_limit', '2.0'))
        add_diff_from_config = eval(get_param('stock_account.add_diff', 'False'))

        for invoice in self:
            if invoice.type in ['in_invoice', 'in_refund']:
                for line in invoice.invoice_line_ids:
                    if line.product_id.cost_method == 'standard':
                        add_diff = True  # daca pretul este standard se inregistreaza diferentele de pret.
                    else:
                        add_diff = add_diff_from_config

                    # daca linia a fost receptionata   de pe baza de aviz se seteaza contul 408 pe nota contabile
                    if account_id and line.account_id == account_id:
                        add_diff = True  # trebuie sa adaug diferenta dintre recpetia pe baza de aviz si receptia din factura

                    if not add_diff:
                        # se reevalueaza stocul
                        price_diff = line.get_stock_valuation_difference()
                        if price_diff:
                            line.modify_stock_valuation(price_diff)

        lines_vals_list = super(AccountInvoice, self)._stock_account_prepare_anglo_saxon_in_lines_vals()

        return lines_vals_list

    def _stock_account_prepare_anglo_saxon_out_lines_vals(self):
        # nu se mai face descarcarea de gestiune la facturare
        return []


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    def _get_computed_account(self):
        if self.product_id.type == "product" and self.move_id.company_id.anglo_saxon_accounting and self.move_id.is_purchase_document():
            purchase = self.move_id.purchase_id
            if self.product_id.purchase_method == "receive":
                # Control bills based on received quantities
                if self.product_id.type == "product":
                    if any([picking.notice for picking in purchase.picking_ids]):
                        self = self.with_context(notice=True)

        return super(AccountInvoiceLine, self)._get_computed_account()

    def get_stock_valuation_difference(self):
        """ Se obtine diferenta dintre evaloarea stocului si valoarea din factura"""
        line = self
        move = line.move_id

        po_currency = line.purchase_line_id.currency_id
        po_company = line.purchase_line_id.company_id

        # Retrieve stock valuation moves.
        valuation_stock_moves = self.env['stock.move'].search([
            ('purchase_line_id', '=', line.purchase_line_id.id),
            ('state', '=', 'done'),
            ('product_qty', '!=', 0.0),
        ])
        if move.type == 'in_refund':
            valuation_stock_moves = valuation_stock_moves.filtered(lambda stock_move: stock_move._is_out())
        else:
            valuation_stock_moves = valuation_stock_moves.filtered(lambda stock_move: stock_move._is_in())

        if not valuation_stock_moves:
            return 0.0

        valuation_price_unit_total = 0
        valuation_total_qty = 0
        for val_stock_move in valuation_stock_moves:
            # In case val_stock_move is a return move, its valuation entries have been made with the
            # currency rate corresponding to the original stock move
            valuation_date = val_stock_move.origin_returned_move_id.date or val_stock_move.date
            svl = val_stock_move.mapped('stock_valuation_layer_ids').filtered(lambda l: l.quantity)
            layers_qty = sum(svl.mapped('quantity'))
            layers_values = sum(svl.mapped('value'))

            valuation_price_unit_total += layers_values
            valuation_total_qty += layers_qty

        precision_rounding = line.product_uom_id.rounding or line.product_id.uom_id.rounding
        if float_is_zero(valuation_total_qty, precision_rounding=precision_rounding):
            return 0.0

        valuation_price_unit = valuation_price_unit_total / valuation_total_qty

        print('Pretul din receptie este: ', valuation_price_unit)

        price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
        if line.tax_ids:
            price_unit = line.tax_ids.compute_all(
                price_unit, currency=move.currency_id, quantity=1.0, is_refund=move.type == 'in_refund')[
                'total_excluded']

        price_unit = line.product_uom_id._compute_price(price_unit, line.product_id.uom_id)

        price_unit = move.currency_id._convert(
            price_unit, move.company_currency_id,
            move.company_id, move.invoice_date, round=False,
        )
        print('Pretul din factura este convertit in moneda companiei: ', price_unit)

        price_unit_val_dif = (price_unit - valuation_price_unit)
        return price_unit_val_dif

    def modify_stock_valuation(self, price_unit_val_dif):
        # se adauga la evaluarea miscarii de stoc

        valuation_stock_move = self.env['stock.move'].search([
            ('purchase_line_id', '=', self.purchase_line_id.id),
            ('state', '=', 'done'),
            ('product_qty', '!=', 0.0),
        ], limit=1)
        linked_layer = valuation_stock_move.stock_valuation_layer_ids[:1]
        value = price_unit_val_dif * self.quantity

        # trebuie cantitate din factura in unitatea produsului si apoi

        value = self.product_uom_id._compute_price(value, self.product_id.uom_id)

        valuation_layer = self.env['stock.valuation.layer'].create({
            'value': value,
            'unit_cost': 0,
            'quantity': 0.000000000000001,
            # in _stock_account_prepare_anglo_saxon_in_lines_vals se face filtrarea dupa cantitate
            'remaining_qty': 0,
            'stock_valuation_layer_id': linked_layer.id,
            'description': _('Price difference'),
            'stock_move_id': valuation_stock_move.id,
            'product_id': self.product_id.id,
            'company_id': self.move_id.company_id.id,
        })

        # todo de eliminat cantitatea dupa ce se apeleaza _stock_account_prepare_anglo_saxon_in_lines_vals
