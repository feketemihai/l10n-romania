# Copyright (C) 2020 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import random
from odoo.tests import Form
from .common import TestStockCommon




class TestStockSale(TestStockCommon):


    def test_plus_inventory(self):
        self.make_puchase()

        inventory = self.env['stock.inventory'].create({
            'location_ids': [(4, self.location_warehouse.id)],
            'product_ids': [(4, self.product_1.id)],
        })
        inventory.action_start()

        inventory.line_ids.product_qty = self.qty_po_p1 + 10
        print ('start plus inventar')
        inventory.action_validate()

        val_stock_p1 = round((self.qty_po_p1 + 10) * self.price_p1, 2)
        val_stock_p2 = round((self.qty_po_p2) * self.price_p2, 2)

        self.check_stock_valuation(val_stock_p1, val_stock_p2)
        self.check_account_valuation(val_stock_p1, val_stock_p2)



    def test_minus_inventory(self):
        self.make_puchase()

        inventory = self.env['stock.inventory'].create({
            'location_ids': [(4, self.location_warehouse.id)],
            'product_ids': [(4, self.product_1.id)],
        })
        inventory.action_start()

        inventory.line_ids.product_qty = self.qty_po_p1 - 10
        print('start minus inventar')
        inventory.action_validate()

        val_stock_p1 = round((self.qty_po_p1 - 10) * self.price_p1, 2)
        val_stock_p2 = round((self.qty_po_p2) * self.price_p2, 2)

        self.check_stock_valuation(val_stock_p1, val_stock_p2)
        self.check_account_valuation(val_stock_p1, val_stock_p2)