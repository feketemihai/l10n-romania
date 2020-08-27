# Copyright (C) 2020 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import random
from odoo.tests import Form
from .common import TestStockCommon

# Generare note contabile la achizitie

class TestStockSale(TestStockCommon):



    def make_puchase(self):


        self.create_po()
        self.create_invoice()





    def create_so(self, notice=False):
        so = Form(self.env["sale.order"])
        so.partner_id = self.client

        with so.order_line.new() as so_line:
            so_line.product_id = self.product_1
            so_line.product_uom_qty = self.qty_so_p1


        with so.order_line.new() as so_line:
            so_line.product_id = self.product_2
            so_line.product_uom_qty = self.qty_so_p2


        self.so = so.save()
        self.so.action_confirm()

        self.picking = self.so.picking_ids
        self.picking.action_assign()  # verifica disponibilitate

        for move_line in self.picking.move_lines:
            if move_line.product_uom_qty > 0 and move_line.quantity_done == 0:
                move_line.write({'quantity_done': move_line.product_uom_qty})



        #self.picking.move_lines.write({'quantity_done': 2})
        #self.picking.button_validate()
        self.picking.action_done()

    def create_sale_invoice(self, diff_p1=0, diff_p2=0):
        # invoice on order
        invoice = self.so._create_invoices()

        invoice = Form(invoice)


        with invoice.invoice_line_ids.edit(0) as line_form:
            line_form.price_unit += diff_p1
        with invoice.invoice_line_ids.edit(1) as line_form:
            line_form.price_unit += diff_p2

        invoice = invoice.save()

        invoice.post()


    def test_sale_and_invoice(self):
        """
             - in stoc valoarea de achiztie din factura
             - in contabilitate valoarea de vanzare
             - in diferente de pret difertnea dintre valoarea de achiztie finala si valoarea de vanzare fara tva
             - in TVA neexigibilă valoarea de tva avand ca baza valoarea de vanzare

        """



        self.make_puchase()

        self.check_stock_valuation(self.val_p1_i, self.val_p2_i)
        self.check_account_valuation(self.val_p1_i, self.val_p2_i)

        self.create_so()
        #self.env.cr.commit()

        val_stock_p1 = round(self.val_p1_i - self.val_so_p1_s,2)
        val_stock_p2 = round(self.val_p2_i - self.val_so_p2_s,2)

        self.check_stock_valuation(val_stock_p1, val_stock_p2)

        # inca nu se face si descaracarea contabila de gestiune!
        self.check_account_valuation(val_stock_p1, val_stock_p2)

        self.create_sale_invoice()


        self.check_stock_valuation(val_stock_p1, val_stock_p2)
        self.check_account_valuation(val_stock_p1, val_stock_p2)

