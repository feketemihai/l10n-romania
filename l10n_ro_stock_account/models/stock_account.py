# -*- coding: utf-8 -*-
# ©  2008-2020 Fekete Mihai <mihai.fekete@forbiom.eu>
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = "stock.move"

    # Exista standard account_move_ids
    # acc_move_id = fields.Many2one('account.move', string='Account move', copy=False)

    # la ce este bun acest camp ?
    #acc_move_line_ids = fields.One2many('account.move.line', 'stock_move_id', string='Account move lines')
    # campul move_type exista in standard
    stock_move_type = fields.Selection([
        ('reception', 'Reception'),
        ('reception_notice', 'Reception with notice'),  # receptie pe baza de aviz
        ('reception_store', 'Reception in store'),  # receptie in magazin
        ('reception_refund', 'Reception refund'),  # rambursare receptie
        ('reception_refund_notice', 'Reception refund with notice'),  # rabursare receptie facuta cu aviz
        ('reception_refund_store_notice', 'Reception refund in store with notice'),
        # rabursare receptie in magazin facuta cu aviz
        ('reception_store_notice', 'Reception in store with notice'),

        ('delivery', 'Delivery'),
        ('delivery_notice', 'Delivery with notice'),
        ('delivery_store', 'Delivery from store'),
        ('delivery_store_notice', 'Delivery from store with notice'),
        ('delivery_refund', 'Delivery refund'),
        ('delivery_refund_notice', 'Delivery refund with notice'),
        ('delivery_refund_store', 'Delivery refund in store'),
        ('delivery_refund_store_notice', 'Delivery refund in store with notice'),
        ('consume', 'Consume'),
        ('inventory_plus', 'Inventory plus'),
        ('inventory_plus_store', 'Inventory plus in store'),
        ('inventory_minus', 'Inventory minus'),
        ('inventory_minus_store', 'Inventory minus in store'),
        ('production', 'Reception from production'),
        ('transfer', 'Transfer'),
        ('transfer_store', 'Transfer in Store'),
        ('transfer_in', 'Transfer in'),
        ('transfer_out', 'Transfer out'),
        ('consume_store', 'Consume from Store'),
        ('production_store', 'Reception in store from production')
    ], compute='_compute_stock_move_type')


    #def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id):
    def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
        if credit_account_id and not isinstance(credit_account_id, int):
            credit_account_id = credit_account_id.id

        if debit_account_id and not isinstance(debit_account_id, int):
            debit_account_id = debit_account_id.id

        debit = self.env['account.account'].browse(debit_account_id)
        credit = self.env['account.account'].browse(credit_account_id)
        _logger.info('NC: %s  = %s   ' % (debit.display_name, credit.display_name))

        permit_same_account = self.env.context.get('permit_same_account', False)
        if credit_account_id != debit_account_id or permit_same_account:
            super(StockMove, self)._create_account_move_line(credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost)


    @api.depends('location_id', 'location_dest_id')
    def _compute_stock_move_type(self):
        for move in self:
            move.stock_move_type = move.get_stock_move_type()


    def get_stock_move_type(self):

        move = self
        location_from = self.location_id
        location_to = self.location_dest_id
        notice = move.picking_id and move.picking_id.notice

        if notice:
            if (location_from.usage == 'internal' and location_to.usage == 'supplier') or \
                    (location_from.usage == 'supplier' and location_to.usage == 'internal'):
                if move.product_id.purchase_method != 'receive':
                    notice = False
                    _logger.warning('La pentru produsul %s nu se poate face receptia pe baza de aviz '
                                    % move.product_id.display_name)

            if (location_from.usage == 'internal' and location_to.usage == 'customer') or \
                    (location_from.usage == 'customer' and location_to.usage == 'internal'):
                if move.product_id.invoice_policy != 'delivery':
                    notice = False
                    _logger.warning('Pentru produsul %s nu se poate utiliza livrare pe baza de aviz '
                                    % move.product_id.display_name)

        move_type = ''
        if location_from.usage == 'supplier' and location_to.usage == 'internal':
            move_type = 'reception'
        elif location_from.usage == 'internal' and location_to.usage == 'supplier':
            move_type = 'reception_refund'
        elif location_from.usage == 'internal' and location_to.usage == 'customer':
            move_type = 'delivery'
        elif location_from.usage == 'customer' and location_to.usage == 'internal':
            move_type = 'delivery_refund'
        elif location_from.usage == 'internal' and location_to.usage == 'production':
            move_type = 'consume'
        elif location_from.usage == 'inventory' and location_to.usage == 'internal':
            move_type = 'inventory_plus'
        elif location_from.usage == 'internal' and location_to.usage == 'inventory':
            move_type = 'inventory_minus'
        elif location_from.usage == 'production' and location_to.usage == 'internal':
            move_type = 'production'
        elif location_from.usage == 'internal' and location_to.usage == 'internal':
            move_type = 'transfer'
        elif location_from.usage == 'internal' and location_to.usage == 'transit':
            if move.picking_id.partner_id.commercial_partner_id != move.company_id.partner_id:
                move_type = 'delivery'
            else:
                move_type = 'transit_out'
        elif location_from.usage == 'transit' and location_to.usage == 'internal':
            if move.picking_id.partner_id.commercial_partner_id != move.company_id.partner_id:
                move_type = 'reception'
            else:
                move_type = 'transit_in'

        if location_from.merchandise_type == 'store' or location_to.merchandise_type == 'store':
            move_type += '_store'
        if notice:
            move_type += '_notice'

        return move_type


    # Modificare conturi determinate standard
    def _get_accounting_data_for_valuation(self):
        journal_id, acc_src, acc_dest, acc_valuation = super(StockMove, self)._get_accounting_data_for_valuation()

        self.ensure_one()
        move = self

        # move_type = self.env.context.get('move_type', move.get_move_type())
        stock_move_type = self.env.context.get('stock_move_type', move.stock_move_type)

        if stock_move_type == 'inventory_plus_store':
            if move.location_dest_id.valuation_in_account_id:
                acc_valuation = move.location_dest_id.valuation_in_account_id
            if move.location_dest_id.property_account_expense_location_id:
                acc_dest = move.location_dest_id.property_account_expense_location_id
                acc_src = acc_dest
        if stock_move_type == 'inventory_minus_store':
            if move.location_id.valuation_out_account_id:
                acc_valuation = move.location_id.valuation_out_account_id
            if move.location_id.property_account_expense_location_id:  # 758800 Alte venituri din exploatare
                acc_dest = move.location_id.property_account_expense_location_id
                acc_src = acc_dest


        if 'delivery_store' in stock_move_type:   # la livrarea din magazin se va folosi contrul specificat in locatie!
            if move.location_id.valuation_out_account_id:  # produsele sunt evaluate dupa contrul de evaluare din locatie
                acc_valuation = move.location_id.valuation_out_account_id

        if 'reception' in stock_move_type and 'notice' in stock_move_type:
            acc_src = move.company_id.property_stock_picking_payable_account_id
            acc_dest = move.company_id.property_stock_picking_payable_account_id

        if 'consume' in stock_move_type or 'delivery' in stock_move_type or 'production' in stock_move_type:
            acc_dest = move.product_id.property_account_expense_id
            if not acc_dest:
                acc_dest = move.product_id.categ_id.property_account_expense_categ_id
            if move.location_id.property_account_expense_location_id:
                acc_dest = move.location_id.property_account_expense_location_id
            acc_src = acc_dest

        if 'inventory_plus' ==  stock_move_type :
            # cont stoc la cont de cheltuiala
            acc_dest = move.product_id.property_account_expense_id
            if not acc_dest:
                acc_dest = move.product_id.categ_id.property_account_expense_categ_id
            if move.location_id.property_account_expense_location_id:  # 758800 Alte venituri din exploatare
                acc_dest = move.location_id.property_account_expense_location_id
            acc_src = acc_dest

        if 'inventory_minus' == stock_move_type :
            # cont de cheltuiala la cont de stoc
            acc_src = move.product_id.property_account_income_id
            if not acc_src:
                acc_src = move.product_id.categ_id.property_account_income_categ_id
            if move.location_dest_id.property_account_income_location_id:  # 758800 Alte venituri din exploatare
                acc_src = move.location_dest_id.property_account_income_location_id
            acc_dest = acc_src

        # de regula se fac la pretul de stocare!
        return journal_id, acc_src, acc_dest, acc_valuation

class StockReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    to_refund = fields.Boolean(default=True)


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'



    @api.model
    def default_get(self, fields_list):
        res = super(ReturnPicking, self).default_get(fields_list)
        if 'product_return_moves' in res:
            product_return_moves = res['product_return_moves']
            for product_return_move in product_return_moves:
                product_return_move[2]['to_refund'] = True
        return res


class Picking(models.Model):
    _inherit = 'stock.picking'

    acc_move_line_ids = fields.Many2many('account.move.line',
                                         string='Generated accounting lines',
                                         compute='_compute_acc_move_line')



    def _compute_acc_move_line(self):
        for picking in self:
            aml = self.env['account.move.line']
            for move in picking.move_lines:
                aml |= move.account_move_ids
            picking.acc_move_line_ids = aml


