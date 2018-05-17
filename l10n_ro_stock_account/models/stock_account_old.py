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
from odoo.exceptions import UserError




# ----------------------------------------------------------
# Stock Location
# ----------------------------------------------------------


class stock_location(models.Model):
    _name = "stock.location"
    _inherit = "stock.location"

    usage = fields.Selection(selection_add=[('in_custody', 'In Custody'),
                                            ('usage_giving', 'Usage Giving'),
                                            ('consume', 'Consume')],

                             help="""* Supplier Location: Virtual location representing the source location for products coming from your suppliers
                       \n* View: Virtual location used to create a hierarchical structures for your warehouse, aggregating its child locations ; can't directly contain products
                       \n* Internal Location: Physical locations inside your own warehouses,
                       \n* Customer Location: Virtual location representing the destination location for products sent to your customers
                       \n* Inventory: Virtual location serving as counterpart for inventory operations used to correct stock levels (Physical inventories)
                       \n* Procurement: Virtual location serving as temporary counterpart for procurement operations when the source (supplier or production) is not known yet. This location should be empty when the procurement scheduler has finished running.
                       \n* Production: Virtual counterpart location for production operations: this location consumes the raw material and produces finished products
                       \n* Transit Location: Counterpart location that should be used in inter-companies or inter-warehouses operations
                       \n* In Custody: Virtual location for products received in custody
                       \n* Usage Giving: Virtual location for products given in usage
                       \n* In Custody: Virtual location for products consumed beside production.
                      """, index=True)

    merchandise_type = fields.Selection([("store", "Store"), ("warehouse", "Warehouse")], string="Merchandise type",
                                        default="warehouse")

    # locatiile sunt dependente de companie. de ce urmatoarele campuri sunt si ele depdenente de companie ?
    # campul standard valuation_in_account_id nu este company_dependent
    # property_stock_account_input_location_id = fields.Many2one('account.account',
    #                                                            string='Stock Input Account',
    #                                                            help="When doing real-time inventory valuation, counterpart journal items for all incoming stock moves will be posted in this account, unless "
    #                                                                 "there is a specific valuation account set on the source location. When not set on the product, the one from the product category is used.",
    #                                                            company_dependent=True)
    # campul standard este valuation_out_account_id
    # property_stock_account_output_location_id = fields.Many2one('account.account',
    #                                                             string='Stock Output Account',
    #                                                             help="When doing real-time inventory valuation, counterpart journal items for all outgoing stock moves will be posted in this account, unless "
    #                                                                  "there is a specific valuation account set on the destination location. When not set on the product, the one from the product category is used.",
    #                                                             company_dependent=True)
    property_account_creditor_price_difference_location_id = fields.Many2one('account.account',
                                                                             string="Price Difference Account",
                                                                             help="This account will be used to value price difference between purchase price and cost price.",
                                                                             company_dependent=True)
    property_account_income_location_id = fields.Many2one('account.account',
                                                          string="Income Account",
                                                          help="This account will be used to value outgoing stock using sale price.",
                                                          company_dependent=True)
    property_account_expense_location_id = fields.Many2one('account.account',
                                                           string="Expense Account",
                                                           help="This account will be used to value outgoing stock using cost price.",
                                                           company_dependent=True)


        

class stock_move(models.Model):
    _name = "stock.move"
    _inherit = "stock.move"

    # Exista standard account_move_ids
    # acc_move_id = fields.Many2one('account.move', string='Account move', copy=False)
    acc_move_line_ids = fields.One2many('account.move.line', 'stock_move_id', string='Account move lines')





    @api.onchange('date')
    def onchange_date(self):
        if self.picking_id:
            self.date_expected = self.picking_id.date
        super(stock_move, self).onchange_date()



    @api.multi
    def action_done(self):
        res = super(stock_move, self).action_done()
        for move in self:
            if move.picking_id:
                move.write({'date': move.picking_id.date})
        return res

    @api.multi
    def action_cancel(self):
        for move in self:
            if move.account_move_ids :
                move.account_move_ids.button_cancel()
                move.account_move_ids.unlink()
        return super(stock_move, self).action_cancel()

    # metoda rescrisa
    @api.multi
    def _get_accounting_data_for_valuation(self):
        """
        Return the accounts and journal to use to post Journal Entries for the real-time
        valuation of the quant.

        :param context: context dictionary that can explicitly mention the company to consider via the 'force_company' key
        :returns: journal_id, source account, destination account, valuation account
        :raise: osv.except_osv() is any mandatory account or journal is not defined.
        """

        journal_id, acc_src, acc_dest, acc_valuation = super(stock_move, self)._get_accounting_data_for_valuation()
        self.ensure_one()
        context = self.env.context
        move = self

        if move.location_id.usage == 'internal' and move.location_dest_id.usage == 'internal':
            acc_dest = move.product_id.property_stock_account_input or move.product_id.categ_id.property_stock_account_input_categ_id
            if not move.value:
                move.write({'value':move.price_unit * move.product_qty})

        if move.location_id.valuation_out_account_id:
            acc_src = move.location_id.valuation_out_account_id
        if move.location_dest_id.valuation_in_account_id:
            acc_dest = move.location_dest_id.valuation_in_account_id



        # Change accounts to suit romanian stock account moves.
        move_type = self.env.context.get('type', '')

        if move_type:
            if move_type == 'delivery_notice' or move_type == 'delivery_notice_refund':
                # Change the account to the income one (70x) to suit move 418 = 70x
                acc_src = move.product_id.property_account_income_id or move.product_id.categ_id.property_account_income_categ_id
                if move.location_id.property_account_income_location_id:
                    acc_src = move.location_id.property_account_income_location_id
            elif move_type == 'usage_giving':
                # Change the account to the usage giving one defined in
                # company: usualy 8035
                acc_src = acc_dest = move.company_id.property_stock_usage_giving_account_id
            elif move_type == 'receive_custody':
                # Change the account to the receive in custody payable account
                # company: usualy 899
                acc_src = move.company_id.property_stock_picking_custody_account_id
            elif move_type == 'custody_to_stock':
                # Change the account to the receive in custody payable account
                # company: usualy 899
                acc_dest = move.company_id.property_stock_picking_custody_account_id
            elif move_type == 'usage_giving':
                # Change the account to the usage giving one defined in
                # company: usualy 8035
                acc_src = acc_dest = move.company_id.property_stock_usage_giving_account_id
            elif move_type == 'delivery':
                # in anglo_saxon_accounting miscarea de stoc se face pe documentrul de facutra
                if not self.company_id.anglo_saxon_accounting:
                    # Change the account to the expense one (6xx) to suit move: 6xx = 3xx
                    acc_dest = move.product_id.property_account_expense_id
                    if not acc_dest:
                        acc_dest = move.product_id.categ_id.property_account_expense_categ_id
                    # daca nu e cont de cheltuiala este contul de iesire din stoc produse finite 711 = 334

                    if not acc_dest:
                        acc_dest = move.product_id.property_stock_account_output or move.product_id.categ_id.property_stock_account_output_categ_id

                    if move.location_id.property_account_expense_location_id:
                        acc_dest = move.location_id.property_account_expense_location_id
            elif move_type == 'inventory':
                # Inventory in plus
                # Change the account to the expense one (6xx) to suit move: 3xx = 6xx
                acc_src = move.product_id.property_account_expense_id or move.product_id.categ_id.property_account_expense_categ_id
                if not acc_src:
                    acc_src = move.product_id.property_stock_account_input or move.product_id.categ_id.property_stock_account_input_categ_id
                if move.location_id.property_account_expense_location_id:
                    acc_src = move.location_id.property_account_expense_location_id
                if move.location_dest_id.property_account_expense_location_id:
                    acc_src = move.location_dest_id.property_account_expense_location_id
            elif move_type in ('inventory_exp', 'delivery_refund'):
                # Inventory with minus and return of delivery
                # Change the account to the expense one (6xx) to suit move: 6xx  = 3xx
                if move_type == 'delivery_refund':
                    acc_src = acc_dest
                acc_dest = move.product_id.property_account_expense_id
                if not acc_dest:
                    acc_dest = move.product_id.categ_id.property_account_expense_categ_id
                if move.location_id.property_account_expense_location_id:
                    acc_dest = move.location_id.property_account_expense_location_id
            elif move_type == 'inventory_vat':
                # Inventory with minus - collect vat
                # Change the accounts with the vat one (442700) and
                # undeductible one defined in company (usualy 635000) to suit
                # move: 635000 = 442700
                taxes_ids = move.product_id.taxes_id.filtered(lambda r: r.company_id == move.company_id)
                if taxes_ids and taxes_ids[0].account_id:
                    acc_src = taxes_ids[0].account_id
                if move.company_id.property_undeductible_tax_account_id:
                    acc_dest = move.company_id and move.company_id.property_undeductible_tax_account_id
            elif move_type == 'reception_diff':
                # Receptions in location with inventory kept at list price
                # Change the accounts with the price difference one (3x8) to  suit move: 3xx = 3x8
                acc_src = move.product_id.property_account_creditor_price_difference
                if not acc_src:
                    acc_src = move.product_id.categ_id.property_account_creditor_price_difference_categ
                if move.location_dest_id.property_account_creditor_price_difference_location_id:
                    acc_src = move.location_dest_id.property_account_creditor_price_difference_location_id

            elif move_type == 'reception_diff_vat':
                # Receptions in location with inventory kept at list price
                # Change the accounts with the uneligible vat one (442810) to
                # suit move: 3xx = 442810
                taxes_ids = move.product_id.supplier_taxes_id.filtered(lambda r: r.company_id == move.company_id)
                if taxes_ids and taxes_ids[0].cash_basis_account:
                    acc_src = taxes_ids[0].cash_basis_account
                else:
                    acc_src = False

            elif move_type == 'delivery_diff':
                # Deliveries from location with inventory kept at list price
                # Change the accounts with the price difference one (3x8) to
                # suit move: 3x8 = 3xx
                acc_dest = move.product_id.property_account_creditor_price_difference
                if not acc_dest:
                    acc_dest = move.product_id.categ_id.property_account_creditor_price_difference_categ
                if move.location_dest_id.property_account_creditor_price_difference_location_id:
                    acc_dest = move.location_dest_id.property_account_creditor_price_difference_location_id

            elif move_type == 'delivery_diff_vat':
                # Deliveries from location with inventory kept at list price
                # Change the accounts with the uneligible vat one (442810) to
                # suit move: 442810 = 3xx
                taxes_ids = move.product_id.taxes_id.filtered(lambda r: r.company_id == move.company_id)
                if taxes_ids and taxes_ids[0].cash_basis_account:
                    acc_dest = taxes_ids[0].cash_basis_account
                else:
                    acc_dest = False

        # If it is a notice, check if picking type is incoming or outgoing and
        # replace the stock accounts with the payable / receivable notice
        # accounts
        if context.get('notice', False):
            if move_type == 'delivery_notice_refund':
                acc_dest = move.company_id and move.company_id.property_stock_picking_receivable_account_id
            elif move_type == 'reception_notice_refund':
                acc_src = move.company_id and move.company_id.property_stock_picking_payable_account_id
            else:
                if move_type not in ['reception_diff']:
                    if move.company_id.property_stock_picking_payable_account_id:
                        if move.location_id.usage == 'supplier':
                            acc_src = move.company_id.property_stock_picking_payable_account_id
                        if move.location_dest_id.usage == 'supplier':
                            acc_dest = move.company_id.property_stock_picking_payable_account_id
                    if move.company_id.property_stock_picking_receivable_account_id:
                        if move.location_dest_id.usage == 'customer':
                            acc_dest = move.company_id.property_stock_picking_receivable_account_id
                        if move.location_id.usage == 'customer':
                            acc_src = move.company_id.property_stock_picking_receivable_account_id

        if acc_src and not isinstance(acc_src, int):
            acc_src = acc_src.id
        if acc_dest and not isinstance(acc_dest, int):
            acc_dest = acc_dest.id

        return journal_id, acc_src, acc_dest, acc_valuation

    def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id):
        if credit_account_id != debit_account_id:
            super(stock_move, self)._create_account_move_line(credit_account_id, debit_account_id, journal_id)


    # metoda mostenita !!
    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id):
        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given quant.
        """
        self.ensure_one()
        move = self
        res = super(stock_move, self)._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id)

        if not res:
            return res
        debit_line_vals = res[0][2]
        credit_line_vals = res[1][2]

        debit_line_vals['stock_move_id'] = move.id
        credit_line_vals['stock_move_id'] = move.id

        if move.picking_id:
            debit_line_vals['stock_picking_id'] = move.picking_id.id
            credit_line_vals['stock_picking_id'] = move.picking_id.id

        if move.inventory_id:
            debit_line_vals['stock_inventory_id'] = move.inventory_id.id
            credit_line_vals['stock_inventory_id'] = move.inventory_id.id

        currency_obj = self.env['res.currency']

        # Calculate VAT base and amount for price differences and associate it
        # to account move lines
        context = self.env.context

        if context.get('type', False)  in ('reception_diff', 'reception_diff_vat',
                                           'delivery_diff', 'delivery_diff_vat'):
            if context.get('force_valuation_amount'):
                valuation_amount = context.get('force_valuation_amount')
            else:
                valuation_amount = move.product_id.cost_method == 'fifo' and cost / qty or move.product_id.standard_price
                valuation_amount = abs(valuation_amount)
            list_price = move.product_id.list_price or 0.00
            if list_price <= valuation_amount:
                raise UserError(_(
                    "You cannot receive products if list price is lower than cost price. Please update list price to suit to be upper than %s." % valuation_amount))
            else:
                # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
                # the company currency... so we need to use round() before
                # creating the accounting entries.
                valuation_amount = list_price * abs(qty) - move.company_id.currency_id.round(valuation_amount * abs(qty))
                taxes = []
                taxes_ids = move.product_id.taxes_id.filtered(lambda r: r.company_id == move.company_id)
                if taxes_ids:
                    taxes = taxes_ids.compute_all(valuation_amount, product=move.product_id)

                if taxes:
                    tax = taxes['taxes'][0]
                    if context.get('type') in ('reception_diff', 'reception_diff_vat'):
                        # Receptions in location with inventory kept at list
                        # price
                        if context.get('type') == 'reception_diff':
                            # debit_line_vals['tax_code_id'] = self.pool.get('account.tax.code').browse(cr, uid, tax['base_code_id']).uneligible_tax_code_id and \
                            #                                 self.pool.get('account.tax.code').browse(cr, uid, tax['base_code_id']).uneligible_tax_code_id.id or False
                            #debit_line_vals['tax_code_id'] = tax['id']  # todo: de verificat campul poate e tax_line_id
                            #debit_line_vals['tax_amount'] = valuation_amount  # de verificat poate e tax_base_amount
                            debit_line_vals['debit'] = valuation_amount
                            debit_line_vals['credit'] = 0.00
                            credit_line_vals['credit'] = valuation_amount
                            credit_line_vals['debit'] = 0.00
                        else:
                            # debit_line_vals['tax_code_id'] = self.pool.get('account.tax.code').browse(cr, uid, tax['tax_code_id']).uneligible_tax_code_id and \
                            #                                 self.pool.get( 'account.tax.code').browse(cr, uid, tax['tax_code_id']).uneligible_tax_code_id.id or False
                            #debit_line_vals['tax_code_id'] = tax['id']
                            #debit_line_vals['tax_amount'] = tax['amount']
                            debit_line_vals['debit'] = tax['amount'] > 0 and round(tax['amount'], 2) or 0.00
                            debit_line_vals['credit'] = tax['amount'] < 0 and -1 * round(tax['amount'], 2) or 0.00
                            credit_line_vals['credit'] = tax['amount'] > 0 and round(tax['amount'], 2) or 0.00
                            credit_line_vals['debit'] = tax['amount'] < 0 and -1 * round(tax['amount'], 2) or 0.00
                    if context.get('type') in ('delivery_diff', 'delivery_diff_vat'):
                        # Deliveries from location with inventory kept at list
                        # price
                        if context.get('type') == 'delivery_diff':
                            # credit_line_vals['tax_code_id'] = self.pool.get('account.tax.code').browse(cr, uid, tax[ 'base_code_id']).uneligible_tax_code_id and \
                            #                                  self.pool.get( 'account.tax.code').browse(cr, uid, tax['base_code_id']).uneligible_tax_code_id.id or False
                            #debit_line_vals['tax_code_id'] = tax['id']
                            #credit_line_vals['tax_amount'] = valuation_amount
                            debit_line_vals['debit'] = valuation_amount
                            debit_line_vals['credit'] = 0.00
                            credit_line_vals['credit'] = valuation_amount
                            credit_line_vals['debit'] = 0.00
                        else:
                            # credit_line_vals['tax_code_id'] = self.pool.get('account.tax.code').browse(cr, uid, tax['tax_code_id']).uneligible_tax_code_id and \
                            #                                  self.pool.get( 'account.tax.code').browse(cr, uid, tax['tax_code_id']).uneligible_tax_code_id.id or False
                            #debit_line_vals['tax_code_id'] = tax['id']
                            #credit_line_vals['tax_amount'] = tax['amount']
                            debit_line_vals['debit'] = tax['amount'] > 0 and round(tax['amount'], 2) or 0.00
                            debit_line_vals['credit'] = tax['amount'] < 0 and -1 * round(tax['amount'], 2) or 0.00
                            credit_line_vals['credit'] = tax['amount'] > 0 and round(tax['amount'], 2) or 0.00
                            credit_line_vals['debit'] = tax['amount'] < 0 and -1 * round(tax['amount'], 2) or 0.00

        # Calculate VAT base and amount for minus in inventories and associate
        # it to account move lines
        if context.get('type', False) and (
                        context.get('type') == 'inventory_exp' or context.get('type') == 'inventory_vat'):
            if context.get('force_valuation_amount'):
                valuation_amount = context.get('force_valuation_amount')
            else:
                valuation_amount = move.product_id.cost_method == 'fifo' and cost or move.product_id.standard_price
            # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
            # the company currency... so we need to use round() before creating
            # the accounting entries.
            valuation_amount = move.company_id.currency_id.round(valuation_amount * qty)
            taxes = []
            taxes_ids = move.product_id.taxes_id.filtered(lambda r: r.company_id == move.company_id)
            if taxes_ids:
                taxes = taxes_ids.compute_all(valuation_amount, product=move.product_id)

            if taxes:
                tax = taxes['taxes'][0]
                if context.get('type') == 'inventory_exp':
                    credit_line_vals['tax_code_id'] = tax['id']
                    credit_line_vals['tax_amount'] = valuation_amount
                else:
                    credit_line_vals['tax_code_id'] = tax['id']
                    credit_line_vals['tax_amount'] = tax['amount']
                    credit_line_vals['account_id'] = tax['account_id']
                    debit_line_vals['debit'] = tax['amount'] > 0 and round(tax['amount'], 2) or 0.00
                    debit_line_vals['credit'] = tax['amount'] < 0 and -1 * round(tax['amount'], 2) or 0.00
                    credit_line_vals['credit'] = tax['amount'] > 0 and round(tax['amount'], 2) or 0.00
                    credit_line_vals['debit'] = tax['amount'] < 0 and -1 * round(tax['amount'], 2) or 0.00

        # Change the amount in case of delivery with notice to price unit
        # invoice
        if context.get('type', False) and (context.get('type') in ('delivery_notice', 'delivery_notice_refund')):
            valuation_amount = cost
            if move.sale_line_id:
                sale_line = move.sale_line_id
                # cum sa fie alt produs in livrare
                if move.product_id.id != sale_line.product_id.id:
                    price_invoice = self.env['product.pricelist'].price_get([sale_line.order_id.pricelist_id.id],
                                                                            move.product_id.id,
                                                                            move.product_uom_qty or 1.0,
                                                                            sale_line.order_id.partner_id)[
                        sale_line.order_id.pricelist_id.id]
                else:
                    price_invoice = sale_line.price_unit
                price_invoice = currency_obj._get_conversion_rate(sale_line.order_id.currency_id,
                                                                  move.company_id.currency_id) * price_invoice
                valuation_amount = price_invoice * abs(qty)
            debit_line_vals['debit'] = valuation_amount
            debit_line_vals['credit'] = 0.00
            credit_line_vals['credit'] = valuation_amount
            credit_line_vals['debit'] = 0.00

        # Change the amounts to be with minus in case of delivery refund
        if context.get('type', False) and (
                    context.get('type') in ('delivery_refund', 'delivery_notice_refund', 'reception_notice_refund')):

            ir_module = self.env['ir.module.module']
            account_storno = False
            module = ir_module.search([('name', '=', 'account_storno')])
            if module:
                account_storno = module.state in ('installed', 'to install', 'to upgrade')
            if account_storno:
                debit_line_vals['debit'] *= -1
                debit_line_vals['credit'] *= -1
                credit_line_vals['credit'] *= -1
                credit_line_vals['debit'] *= -1
            else:
                debit_line_vals['debit'], debit_line_vals['credit'] = debit_line_vals['credit'], debit_line_vals[
                    'debit']
                credit_line_vals['credit'], credit_line_vals['debit'] = credit_line_vals['debit'], credit_line_vals[
                    'credit']

        return [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]

    def _account_entry_move(self):
        """ Accounting Valuation Entries """
        self.ensure_one()
        move = self

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

        # in case of routes making the link between several warehouse of the same company, the transit location belongs
        # to this company, so we don't need to create accounting entries
        # Create Journal Entry for stock moves
        ctx = self.env.context.copy()
        if company_to:
            if location_from.usage in ('supplier', 'customer'):
                ctx['force_company'] = company_to.id
        if company_from:
            if location_to.usage in ('supplier', 'customer'):
                ctx['force_company'] = company_from.id
        # Put notice in context if the picking is a notice
        ctx['notice'] = move.picking_id and move.picking_id.notice

        if ctx['notice']:
            if (location_from.usage == 'internal' and location_to.usage == 'supplier') or \
                    (location_from.usage == 'supplier' and location_to.usage == 'internal'):
                ctx['notice'] = move.product_id.purchase_method == 'receive'

            if (location_from.usage == 'internal' and location_to.usage == 'customer') or \
                    (location_from.usage == 'customer' and location_to.usage == 'internal'):
                ctx['notice'] = move.product_id.invoice_policy == 'delivery'

        if ctx['notice'] and location_from.usage == 'internal' and location_to.usage == 'supplier':
            ctx['type'] = 'reception_notice_refund'

        # Create account moves for price difference and uneligible VAT is inventory of one the location is kept at list price.
        # To do : intercompany moves.
        if (location_from.usage == 'internal' and location_from.merchandise_type == 'store') \
                or (location_to.usage == 'internal' and location_to.merchandise_type == 'store'):
            # Create moves for entry to stock location with merchandise type ==  store
            if (location_from.usage != 'internal' or
                    (location_from.usage == 'internal' and location_from.merchandise_type != 'store')) and \
                    (location_to.usage == 'internal' and location_to.merchandise_type == 'store'):
                ctx['type'] = 'reception_diff'
                move = move.with_context(ctx)
                journal_id, acc_src, acc_dest, acc_valuation = move._get_accounting_data_for_valuation()
                if acc_src and acc_dest and acc_src != acc_dest:
                    move._create_account_move_line(acc_src, acc_dest, journal_id)
                ctx['type'] = 'reception_diff_vat'
                if location_from.usage != 'supplier':
                    move = move.with_context(ctx)
                    journal_id, acc_src, acc_dest, acc_valuation = move._get_accounting_data_for_valuation()
                    if acc_src and acc_dest and acc_src != acc_dest:
                        move._create_account_move_line(acc_src, acc_dest, journal_id)
            # Create moves for outgoing from stock
            if (location_to.usage != 'internal' or
                    (location_to.usage == 'internal' and location_to.merchandise_type != 'store')) and \
                    (location_from.usage == 'internal' and location_from.merchandise_type == 'store'):
                ctx['type'] = 'delivery_diff'
                move = move.with_context(ctx)
                journal_id, acc_src, acc_dest, acc_valuation = move._get_accounting_data_for_valuation()
                if acc_src and acc_dest and acc_src != acc_dest:
                    move._create_account_move_line(acc_src, acc_dest, journal_id)

                ctx['type'] = 'delivery_diff_vat'
                move = move.with_context(ctx)
                journal_id, acc_src, acc_dest, acc_valuation = move._get_accounting_data_for_valuation()
                if acc_src and acc_dest and acc_src != acc_dest:
                    move._create_account_move_line(acc_src, acc_dest, journal_id)

        # Create account moves for deliveries with notice (e.g. 418 = 707)
        if ctx['notice'] and location_from.usage == 'internal' and location_to.usage == 'customer':
            ctx['type'] = 'delivery_notice'
            move = move.with_context(ctx)
            journal_id, acc_src, acc_dest, acc_valuation = move._get_accounting_data_for_valuation()
            if acc_src and acc_dest and acc_src != acc_dest:
                move._create_account_move_line(acc_src, acc_dest, journal_id)

            # Change context to create account moves for cost of goods sold
            # (e.g. 607 = 371)
            ctx['notice'] = False
            ctx['type'] = 'delivery'

        # Create account moves for refund deliveries with notice (e.g. 707 = 418)
        if ctx['notice'] and location_from.usage == 'customer' and location_to.usage == 'internal':
            ctx['type'] = 'delivery_notice_refund'
            move = move.with_context(ctx)
            journal_id, acc_src, acc_dest, acc_valuation = move._get_accounting_data_for_valuation()

            if acc_src and acc_dest and acc_src != acc_dest:
                move._create_account_move_line(acc_src, acc_dest, journal_id)

            # Change context to create account moves for cost of goods sold
            # (e.g. 371 = 607)
            ctx['notice'] = False
            ctx['type'] = 'delivery_refund'

        # Change context to create account moves for cost of goods sold in case
        # of refund (e.g. 371 = 607)
        if not ctx['notice'] and location_from.usage == 'customer' and location_to.usage == 'internal':
            ctx['type'] = 'delivery_refund'

        # Change context to create account moves for cost of goods received in custody - extra trial balance
        # of refund (e.g. 8033 = 899)
        if not ctx['notice'] and location_from.usage == 'supplier' and location_to.usage == 'in_custody':
            ctx['type'] = 'receive_custody'
        if not ctx['notice'] and location_from.usage == 'in_custody' and location_to.usage == 'internal':
            ctx['type'] = 'custody_to_stock'

        if not ctx['notice'] and location_from.usage == 'internal' and location_to.usage not in (
                'supplier', 'transit'):
            # Change context to create account moves for cost of goods
            # delivered  (e.g. 607 = 371)
            ctx['notice'] = False
            if location_to.usage != 'internal':
                ctx['type'] = 'delivery'
            # Change context to create account moves for collected VAT in case
            # of minus in inventory  (e.g. 635 = 4427)
            if location_to.usage == 'inventory':
                ctx['type'] = 'inventory_vat'
                move = move.with_context(ctx)
                journal_id, acc_src, acc_dest, acc_valuation = move._get_accounting_data_for_valuation()
                if acc_src and acc_dest and acc_src != acc_dest:
                    move._create_account_move_line(acc_src, acc_dest, journal_id)

                # Change context to create account moves for minus in inventory
                # (e.g. 607 = 371 with VAT collected based)
                ctx['type'] = 'inventory_exp'
            # Change context to create account moves for usage giving  (e.g.  8035 = 8035)
            if location_to.usage == 'usage_giving':
                ctx['type'] = 'usage_giving'
                move = move.with_context(ctx)
                journal_id, acc_src, acc_dest, acc_valuation = move._get_accounting_data_for_valuation()
                if acc_src and acc_dest and ctx['type'] == 'usage_giving':
                    move._create_account_move_line(acc_src, acc_dest, journal_id)

                # Change context to create account moves for cost of goods
                # delivered  (e.g. 607 = 371)
                ctx['type'] = 'delivery'

        # Change context to create account moves for plus in inventory  (e.g. -607 = -371)
        if not ctx['notice'] and location_from.usage == 'inventory' and location_to.usage == 'internal':
            ctx['notice'] = False
            ctx['type'] = 'inventory'
        move = move.with_context(ctx)
        journal_id, acc_src, acc_dest, acc_valuation = move._get_accounting_data_for_valuation()
        if location_from.usage == 'production' or location_to.usage == 'production':
            pass
        else:
            if acc_src and acc_dest and acc_src != acc_dest:
                move._create_account_move_line(acc_src, acc_dest, journal_id)

        super(stock_move, self)._account_entry_move()


class stock_picking(models.Model):
    _name = 'stock.picking'
    _inherit = 'stock.picking'

    acc_move_line_ids = fields.One2many('account.move.line', 'stock_picking_id', string='Generated accounting lines')

    # prin acest camp se indica daca un produs care e stocabil trece prin contul 408 / 418 la achizitie sau vanzare
    # receptie/ livrare in baza de aviz
    notice = fields.Boolean('Is a notice', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
                            default=False)

    """
    @api.multi
    def get_account_move_lines(self):
        for pick in self:
            acc_move_lines = self.env['account.move.line']
            for move in pick.move_lines:
                if move.acc_move_id:
                    acc_move_lines |= move.acc_move_id.line_id
            if acc_move_lines:
                acc_move_lines.write({'stock_picking_id': pick.id})
        return True
    """

    @api.multi
    def do_transfer(self):
        self.ensure_one()
        for pick in self:
            pick.write({'date_done': pick.date})
        res = super(stock_picking, self).do_transfer()
        # self.get_account_move_lines()
        return res

    @api.multi
    def action_done(self):
        for pick in self:
            pick.write({'date_done': pick.date})
        res = super(stock_picking, self).action_done()
        # self.get_account_move_lines()
        return res

    @api.multi
    def action_cancel(self):
        for pick in self:
            for move in pick.move_lines:
                if move.account_move_ids :
                    move.account_move_ids .button_cancel()
                    move.account_move_ids .unlink()
        return super(stock_picking, self).action_cancel()

    @api.multi
    def action_unlink(self, cr, uid, ids, context=None):
        for pick in self.browse:
            for move in pick.move_lines:
                if move.account_move_ids :
                    move.account_move_ids.button_cancel()
                    move.account_move_ids.unlink()
        return super(stock_picking, self).action_unlink()

    # nu cred ca mai exista in 10.0
    '''
    @api.multi
    def action_invoice_create(self, journal_id, group=False, type='out_invoice'):
        res = super(stock_picking, self).action_invoice_create(journal_id, group, type)
        self.write({'notice': False})
        return res
    '''


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    acc_move_line_ids = fields.One2many('account.move.line', 'stock_inventory_id', string='Generated accounting lines')

    @api.multi
    def post_inventory(self):
        res = super(StockInventory, self).post_inventory()
        for inv in self:
            acc_move_line_ids = self.env['account.move.line']
            for move in inv.move_ids:
                for acc_move in move.account_move_ids:
                    acc_move_line_ids |= acc_move.line_ids
            acc_move_line_ids.write({'stock_inventory_id':inv.id})
        return res
    """
    @api.multi
    def get_account_move_lines(self):
        for inv in self:
            acc_move_lines = self.env['account.move.line']
            for move in inv.move_ids:
                if move.acc_move_id:
                    acc_move_lines |= move.acc_move_id.line_ids

            if acc_move_lines:
                acc_move_lines.write({'stock_inventory_id': inv.id})
        return True


    @api.multi
    def post_inventory(self):
        res = super(StockInventory, self).post_inventory()
        self.get_account_move_lines()
        return res
    """

    @api.multi
    def action_cancel_draft(self):
        for inv in self:
            for move in inv.move_ids:
                if move.account_move_ids:
                    move.account_move_ids.cancel()
                    move.account_move_ids.unlink()
        return super(StockInventory, self).action_cancel_draft()

    @api.multi
    def unlink(self):
        if any(inv.state not in ('draft', 'cancel') for inv in self):
            raise UserError(_('You can only delete draft inventory.'))
        return super(StockInventory, self).unlink()
