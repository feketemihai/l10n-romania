# -*- coding: utf-8 -*-
# ©  2008-2018 Fekete Mihai <mihai.fekete@forbiom.eu>
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import models, fields





"""
class purchase_order(models.Model):
    _inherit = 'purchase.order'

    # todo: care o fi metoda in Odoo10  - pregateste  pretul cu care se va face intrare in stoc
    @api.model
    def _prepare_order_line_move(self, order, order_line,  picking_id, group_id ):
        '''
        prepare the stock move data from the PO line. This function
        returns a list of dictionary ready to be used in stock.move's
        create()
        '''

        res = super(purchase_order, self)._prepare_order_line_move(  order, order_line, picking_id, group_id)
        product_uom = self.pool.get('uom.uom')
        price_unit = order_line.price_unit
        if order_line.product_uom.id != order_line.product_id.uom_id.id:
            price_unit *= order_line.product_uom.factor /  order_line.product_id.uom_id.factor
        ctx = dict(self.env.context)
        ctx.update({'date': order.date_order})
        if order.currency_id.id != order.company_id.currency_id.id:
            #we don't round the price_unit, as we may want to store the
            #standard price with more digits than allowed by the currency
            price_unit = self.pool.get('res.currency').compute(  order.currency_id.id, order.company_id.currency_id.id,  price_unit, round=False)
        for line in res:
            line['price_unit'] = price_unit
        return res
"""

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _prepare_account_move_line(self, move):

        data = super(PurchaseOrderLine, self)._prepare_account_move_line(move)

        line = self

        if line.product_id.purchase_method == 'receive':  # receptia in baza cantitatilor primite
            if line.product_id.type == 'product':
                notice = False
                for picking in line.order_id.picking_ids:
                    if picking.notice:
                        notice = True

                if notice:  # daca e stocabil si exista un document facut
                    data['account_id'] = line.company_id.property_stock_picking_payable_account_id.id or \
                                         line.product_id.categ_id.property_stock_account_input_categ_id.id or \
                                         data['account_id']
                else:
                    data['account_id'] =  line.product_id.categ_id.property_stock_account_input_categ_id.id or \
                                         data['account_id']

            else:  # daca nu este stocabil trebuie sa fie un cont de cheltuiala
                data['account_id'] =  line.product_id.categ_id.property_account_expense_categ_id.id or \
                                     data['account_id']
        else:
            if line.product_id.type == 'product':
                data['account_id'] =  line.product_id.categ_id.property_stock_account_input_categ_id.id or \
                                     data['account_id']

        return data