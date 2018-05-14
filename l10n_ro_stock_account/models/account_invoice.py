# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import AccessError, UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _prepare_invoice_line_from_po_line(self, line):
        data = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        if self.type in ['in_invoice', 'in_refund']:

            if line.product_id.purchase_method == 'receive':  # receptia in baza cantitatilor primite
                if line.product_id.type == 'product':
                    notice = False
                    for picking in line.order_id.picking_ids:
                        if picking.notice:
                            notice = True

                    if notice:  # daca e stocabil si exista un document facut
                        data['account_id'] = line.company_id.property_stock_picking_payable_account_id.id or \
                                             line.product_id.property_stock_account_input.id or \
                                             line.product_id.categ_id.property_stock_account_input_categ_id.id or \
                                             data['account_id']
                    else:
                        data['account_id'] = line.product_id.property_stock_account_input.id or \
                                             line.product_id.categ_id.property_stock_account_input_categ_id.id or \
                                             data['account_id']

                else:  # daca nu este stocabil trebuie sa fie un cont de cheltuiala
                    data['account_id'] = line.product_id.property_account_expense_id.id or \
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


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.onchange('product_id')
    def _onchange_product_id(self):

        if self.product_id and self.product_id.type == 'product' and not self.env.context.get('from_pos_order',False):
            raise UserError(_('Changing the stored product is not allowed!'))
        return super(AccountInvoiceLine, self)._onchange_product_id()

    @api.onchange('quantity')
    def _onchange_quantity(self):
        if self.invoice_id.type in ['in_refund','out_refund']:
            return
        if self.product_id and self.product_id.type == 'product':

            if self.purchase_line_id:
                qty = 0
                for inv_line in self.purchase_line_id.invoice_lines:
                    if not isinstance(inv_line.id, models.NewId) and inv_line.invoice_id.state not in ['cancel']:
                        if inv_line.invoice_id.type == 'in_invoice':
                            qty += inv_line.uom_id._compute_quantity(inv_line.quantity,
                                                                     self.purchase_line_id.product_uom)
                        elif inv_line.invoice_id.type == 'in_refund':
                            qty -= inv_line.uom_id._compute_quantity(inv_line.quantity,
                                                                     self.purchase_line_id.product_uom)

                qty_invoiced = qty

                qty = self.purchase_line_id.qty_received - qty_invoiced

                qty = self.purchase_line_id.product_uom._compute_quantity(qty, self.uom_id)

                if qty < self.quantity:
                    raise UserError(_('Can not record an invoice for a larger quantity of %s') % str(qty))
            else:
                raise UserError(_('Changing quantity of the stored product is not allowed!'))
