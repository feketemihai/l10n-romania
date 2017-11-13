# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _prepare_invoice_line_from_po_line(self, line):
        data = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        if self.type in ['in_invoice','in_refund']:

            if line.product_id.purchase_method == 'receive': # receptia in baza cantitatilor primite
                if line.product_id.type == 'product':
                    ok = False
                    for move in line.move_ids:
                        if move.acc_move_id:
                            ok = True

                    if ok :  # daca e stocabil si exista un doc facut
                        data['account_id'] = line.company_id.property_stock_picking_payable_account_id.id or \
                                             line.product_id.property_stock_account_input.id or \
                                             line.product_id.categ_id.property_stock_account_input_categ_id.id or \
                                             data['account_id']
                    else:
                        data['account_id'] = line.product_id.property_stock_account_input.id or \
                                             line.product_id.categ_id.property_stock_account_input_categ_id.id or \
                                             data['account_id']

                else:  # daca nu este stocabil trebuie sa fie un cont de cheltuiala
                    data['account_id'] = line.company_id.property_stock_picking_payable_account_id.id or \
                                         line.product_id.property_account_expense_id.id or \
                                         line.product_id.categ_id.property_account_expense_categ_id.id or \
                                         data['account_id']
            else:
                if line.product_id.type == 'product':
                    data['account_id'] = line.product_id.property_stock_account_input.id or \
                                         line.product_id.categ_id.property_stock_account_input_categ_id.id or \
                                         data['account_id']

        return data


# metoda locala sau se poate in 10 are alt nume
'''
@api.multi
def _get_invoice_line_vals(self, partner, inv_type):
    move = self
    res = super(stock_move, self)._get_invoice_line_vals(partner, inv_type)

    # For receptions, get the stock account, instead of the expense one.
    account_id = res['account_id']
    if inv_type in ('in_invoice', 'in_refund'):
        account_id = move.product_id.property_stock_account_input and move.product_id.property_stock_account_input.id
        if not account_id:
            account_id = move.product_id.categ_id.property_stock_account_input_categ and move.product_id.categ_id.property_stock_account_input_categ.id
        if move.origin_returned_move_id:
            if move.location_id.property_stock_account_input_location:
                account_id = move.location_id.property_stock_account_input_location and move.location_id.property_stock_account_input_location.id
        else:
            if move.location_dest_id.property_stock_account_input_location:
                account_id = move.location_dest_id.property_stock_account_input_location and move.location_dest_id.property_stock_account_input_location.id
    if move.picking_id and move.picking_id.notice:
        if inv_type in ('in_invoice', 'in_refund'):
            account_id = move.company_id and move.company_id.property_stock_picking_payable_account_id and move.company_id.property_stock_picking_payable_account_id.id
        else:
            account_id = move.company_id and move.company_id.property_stock_picking_receivable_account_id and move.company_id.property_stock_picking_receivable_account_id.id
    fiscal_position = partner.property_account_position
    account_id = fiscal_position.map_account(account_id)
    res['account_id'] = account_id

    # If it is a returned stock move, change quantity in invoice with minus
    # (probably to be done in account_storno)

    if move.origin_returned_move_id:
        account_storno = False
        ir_module = self.env['ir.module.module']
        module = ir_module.search([('name', '=', 'account_storno')])
        if module:
            account_storno = module.state in ('installed', 'to install', 'to upgrade')
        if account_storno:
            res['quantity'] = -1 * res['quantity']
    return res
'''