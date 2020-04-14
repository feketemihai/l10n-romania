# -*- coding: utf-8 -*-
# ©  2008-2018 Fekete Mihai <mihai.fekete@forbiom.eu>
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import AccessError, UserError


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    # nu trebuie sa se schimbe locatia la receptie
    #stock_location_id = fields.Many2one('stock.location', readonly=True, states={'draft': [('readonly', False)]})

    # @api.onchange('purchase_vendor_bill_id', 'purchase_id')
    # def _onchange_purchase_auto_complete(self):
    #     if not self.stock_location_id:
    #         self.stock_location_id = self.purchase_id.picking_type_id.default_location_dest_id
    #     res = super(AccountInvoice, self)._onchange_purchase_auto_complete()
    #     return res

    # codul _prepare_invoice_line_from_po_line (care era in 11) se gaeste in purchase.line metoda   _prepare_account_move_line



    def post(self):
        # OVERRIDE
        # Create additional price difference lines for vendor bills.
        if self._context.get('move_reverse_cancel'):
            return super(AccountInvoice, self).post()
        self.env['account.move.line'].create(self._invoice_line_move_line_get_diff())
        return super(AccountInvoice, self).post()

    # in 13 nu mai exista invoice_line_move_line_get si am folosit

    @api.model
    def _invoice_line_move_line_get_diff(self):

        res = []

        # este setat contul 408 in configurare ?
        account_id = self.company_id.property_stock_picking_payable_account_id
        get_param = self.env['ir.config_parameter'].sudo().get_param
        # char daca nu este sistem anglo saxon diferentele de pret dintre receptie si factura trebuie inregistrate
        if not self.env.user.company_id.anglo_saxon_accounting:
            for invoice in self:
                if invoice.type in ['in_invoice', 'in_refund']:
                    diff_limit = float(get_param('stock_account.diff_limit', '2.0'))

                    # se adaga nota contabilia cu diferanta de pret la achizitie ?

                    add_diff_from_config = eval( get_param('stock_account.add_diff', 'False'))

                    for i_line in invoice.invoice_line_ids:
                        if i_line.product_id.cost_method == 'standard':
                            add_diff = True  # daca pretul este standard se inregistreaza diferentele de pret.
                        else:
                            add_diff = add_diff_from_config

                        # daca linia a fost peceptionata  de pe baza de aviz se seteaza contul 408 pe nota contabile
                        if account_id and i_line.account_id == account_id:
                            i_line = i_line.with_context(fix_stock_input=account_id)
                            add_diff = True  # trbuie sa adaug diferenta dintre recpetia pe baza de aviz si receptia din factura
                        diff_line = self._anglo_saxon_purchase_move_lines(i_line, res)  # nu mai exista aceasta metoda in 13.  exista doar _stock_account_prepare_anglo_saxon_in_lines_vals

                        line_diff_value = 0.0
                        for diff in diff_line:

                            if add_diff:
                                if abs(diff['price_unit'] * diff['quantity']) > diff_limit:
                                    raise UserError(_('The price difference for the product %s exceeds the %d limit ') % (
                                        i_line.product_id.name, diff_limit))

                            else:
                                line_diff_value += diff['price_unit'] * diff['quantity']
                                diff['account_id'] = i_line.account_id.id
                                diff['name'] += _(' Price difference')
                                diff['quantity'] = 0.0  # nu mai este necesara inregistrarea cantitatii

                        if diff_line:
                            res.extend(diff_line)

                        if line_diff_value:
                            i_line.modify_stock_move_value(line_diff_value)

        for invoice in self:
            if invoice.type in ['in_invoice', 'in_refund']:
                res = invoice.trade_discount_distribution(res)

        for line in res:
            line['stock_location_id'] = self.stock_location_id.id

        return res

    def trade_discount_distribution(self, res):

        # distribuire valaore de pe linii cu discount comerical
        account_id = self.company_id.property_trade_discount_received_account_id

        discounts = {}
        discount_lines = self.invoice_line_ids.filtered(lambda x: x.account_id.id == account_id.id)
        for line in discount_lines:
            discounts[line.id] = {
                'line_id': line,
                'amount': line.price_subtotal,
                'rap': 0.0,
                'lines': self.env['account.move.line']
            }
            for aml in res:
                if aml.get('invl_id') == line.id:
                    discounts[line.id]['aml'] = aml

        invoice_lines = []
        for line in self.invoice_line_ids:
            invoice_lines.insert(0, line)
        # pentru ce linii sunt aferente aceste discounturi - sunt luate in calcul liniile de inaintea discountului
        discount = False
        for line in invoice_lines:  ##self.invoice_line_ids.sorted(key=lambda r: r.sequence, reverse=True):
            if line.account_id.id == account_id.id:
                discount = discounts[line.id]
            else:
                # eventual se va adauga o conditie petnru a utiliza dosr conturle care sunt de stoc
                if discount and line.product_id.type == 'product':
                    discount['lines'] |= line

        for line_id in discounts:
            value = 0
            for line in discounts[line_id]['lines']:
                value += line.price_subtotal
            if value:
                rap = discounts[line_id]['amount'] / value
                discounts[line_id]['rap'] = rap

                for line in discounts[line_id]['lines']:
                    for aml in res:
                        if aml.get('invl_id') == line.id:
                            val = aml['price'] * discounts[line_id]['rap']
                            aml['price'] += val
                            discounts[line_id]['aml']['price'] += -val
                            line.modify_stock_move_value(val)

        for aml in res:
            if aml['price'] == 0:
                res.remove(aml)
        return res


    # def finalize_invoice_move_lines(self, move_lines):
    #     move_lines  = super(AccountInvoice, self).finalize_invoice_move_lines(move_lines)
    #
    #     for line in move_lines:
    #         if self.type in ['in_invoice','out_refund']:
    #             line[2]['stock_location_dest_id'] = self.stock_location_id.id
    #         else:
    #             line[2]['stock_location_id'] = self.stock_location_id.id
    #
    #     return move_lines


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    def modify_stock_move_value(self, line_diff_value):
        product = self.product_id  # with_context(to_date=self.move_id.invoice_date)
        if self.product_id and self.product_id.valuation == 'real_time' and self.product_id.type == 'product':
            if self.product_id.cost_method != 'standard' and self.purchase_line_id:
                stock_move_obj = self.env['stock.move']
                valuation_stock_move = stock_move_obj.search([
                    ('purchase_line_id', '=', self.purchase_line_id.id),
                    ('state', '=', 'done'), ('product_qty', '!=', 0.0)
                ])
                if self.move_id.type == 'in_refund':
                    valuation_stock_move = valuation_stock_move.filtered(lambda m: m._is_out())
                elif self.move_id.type == 'in_invoice':
                    valuation_stock_move = valuation_stock_move.filtered(lambda m: m._is_in())

                if valuation_stock_move:
                    for move in valuation_stock_move:
                        cost_to_add = (move.remaining_qty / move.product_qty) * line_diff_value
                        move.write({
                            'value': move.value + line_diff_value,
                            'remaining_value': move.remaining_value + cost_to_add,
                            'price_unit': (move.value + line_diff_value) / move.product_qty,
                        })
                        # todo: de actualizat pretul standard cu noua valoare de stoc

                stock_value = product.stock_value  # + line_diff_value
                new_price = stock_value / product.qty_at_date
                self.product_id.write({'standard_price': new_price})

    @api.onchange('product_id')
    def _onchange_product_id(self):
        # modulul deltatech_invoice_receipt gestioneaza adaugarea de pozitii noi in factura de achzitie
        if self.move_id.type == 'out_invoice':
            if self.product_id and self.product_id.type == 'product' and not self.env.context.get(
                    'allowed_change_product', False):
                raise UserError(_('It is not allowed to change a stored product!'))
        return super(AccountInvoiceLine, self)._onchange_product_id()

    # @api.onchange('quantity')
    # def _onchange_quantity(self):
    #     message = ''
    #     if self.move_id.type in ['in_refund', 'out_refund']:
    #         return
    #     if self.product_id and self.product_id.type == 'product':
    #
    #         if self.purchase_line_id:
    #             qty = 0
    #             for inv_line in self.purchase_line_id.invoice_lines:
    #                 if not isinstance(inv_line.id, models.NewId) and inv_line.move_id.state not in ['cancel']:
    #                     if inv_line.move_id.type == 'in_invoice':
    #                         qty += inv_line.uom_id._compute_quantity(inv_line.quantity,
    #                                                                  self.purchase_line_id.product_uom)
    #                     elif inv_line.move_id.type == 'in_refund':
    #                         qty -= inv_line.uom_id._compute_quantity(inv_line.quantity,
    #                                                                  self.purchase_line_id.product_uom)
    #
    #             qty_invoiced = qty
    #
    #             qty = self.purchase_line_id.qty_received - qty_invoiced
    #
    #             qty = self.purchase_line_id.product_uom._compute_quantity(qty, self.uom_id)
    #
    #             if qty < self.quantity:
    #                 raise UserError(
    #                     _('It is not allowed to record an invoice for a quantity bigger than %s') % str(qty))
    #         else:
    #             message = _('It is not indicated to change the quantity of a stored product!')
    #     if message:
    #         return {
    #             'warning': {'title': "Warning", 'message': message},
    #         }
