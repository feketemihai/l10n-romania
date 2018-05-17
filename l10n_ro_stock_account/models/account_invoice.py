# -*- coding: utf-8 -*-
# ©  2008-2018 Fekete Mihai <mihai.fekete@forbiom.eu>
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import AccessError, UserError




class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    stock_location_id = fields.Many2one('stock.location', readonly=True, states={'draft': [('readonly', False)]})


    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.stock_location_id:
            self.stock_location_id = self.purchase_id.picking_type_id.default_location_dest_id
        res = super(AccountInvoice, self).purchase_order_change()
        return res

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

    @api.model
    def invoice_line_move_line_get(self):
        res = super(AccountInvoice, self).invoice_line_move_line_get()
        for line in res:
            line['stock_location_id'] = self.stock_location_id.id
        return res

    # @api.multi
    # def finalize_invoice_move_lines(self, move_lines):
    #     move_lines = super(AccountInvoice, self).finalize_invoice_move_lines(move_lines)
    #     for move_line in move_lines:
    #         move_line[2]['stock_location_id'] = self.stock_location_id.id
    #     return move_lines


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.onchange('product_id')
    def _onchange_product_id(self):

        if self.product_id and self.product_id.type == 'product' and not self.env.context.get('from_pos_order', False):
            raise UserError(_('Changing the stored product is not allowed!'))
        return super(AccountInvoiceLine, self)._onchange_product_id()

    @api.onchange('quantity')
    def _onchange_quantity(self):
        if self.invoice_id.type in ['in_refund', 'out_refund']:
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
