# Copyright (C) 2020 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import random

from odoo.tests import Form
from odoo.tests.common import SavepointCase

# Generare note contabile la achizitie


class TestStockCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockCommon, cls).setUpClass()

        account_type_inc = cls.env.ref("account.data_account_type_revenue")
        account_type_exp = cls.env.ref("account.data_account_type_expenses")
        account_type_cur = cls.env.ref("account.data_account_type_current_assets")
        account_type_current_liabilities = cls.env.ref("account.data_account_type_current_liabilities")

        cls.account_difference = cls.env["account.account"].search([("code", "=", "348000")], limit=1)
        if not cls.account_difference:
            cls.account_difference = cls.env["account.account"].create(
                {"name": "Difference", "code": "348000", "user_type_id": account_type_cur.id, "reconcile": False,}
            )

        cls.account_expense = cls.env["account.account"].search([("code", "=", "607000")], limit=1)
        if not cls.account_expense:
            cls.account_expense = cls.env["account.account"].create(
                {"name": "Expense", "code": "607000", "user_type_id": account_type_exp.id, "reconcile": False,}
            )

        cls.account_income = cls.env["account.account"].search([("code", "=", "707000")])
        if not cls.account_income:
            cls.account_income = cls.env["account.account"].create(
                {"name": "Income", "code": "707000", "user_type_id": account_type_inc.id, "reconcile": False,}
            )

        # se poate utiliza foarte bine si  408
        cls.account_input = cls.env["account.account"].search([("code", "=", "371000.i")])
        if not cls.account_input:
            cls.account_input = cls.env["account.account"].create(
                {"name": "Income", "code": "371000.i", "user_type_id": account_type_cur.id, "reconcile": False,}
            )

        # se poate utiliza foarte bine si  418
        cls.account_output = cls.env["account.account"].search([("code", "=", "371000.o")])
        if not cls.account_output:
            cls.account_output = cls.env["account.account"].create(
                {"name": "Output", "code": "371000.o", "user_type_id": account_type_cur.id, "reconcile": False,}
            )

        cls.account_valuation = cls.env["account.account"].search([("code", "=", "371000")])
        if not cls.account_valuation:
            cls.account_valuation = cls.env["account.account"].create(
                {"name": "Valuation", "code": "371000", "user_type_id": account_type_cur.id, "reconcile": False,}
            )

        cls.uneligible_tax_account_id = cls.env.user.company_id.tax_cash_basis_journal_id.default_debit_account_id
        if not cls.uneligible_tax_account_id:
            cls.uneligible_tax_account_id = cls.env["account.account"].search([("code", "=", "442810")])
        if not cls.uneligible_tax_account_id:
            cls.uneligible_tax_account_id = cls.env["account.account"].create(
                {
                    "name": "TVA neexigibilă – Colectată",
                    "code": "442810",
                    "user_type_id": account_type_cur.id,
                    "reconcile": False,
                }
            )
        cls.env.user.company_id.tax_cash_basis_journal_id.default_debit_account_id = cls.uneligible_tax_account_id

        cls.stock_picking_payable_account_id = cls.env.user.company_id.property_stock_picking_payable_account_id
        if not cls.stock_picking_payable_account_id:
            cls.stock_picking_payable_account_id = cls.env["account.account"].search([("code", "=", "408000")])
        if not cls.stock_picking_payable_account_id:
            cls.stock_picking_payable_account_id = cls.env["account.account"].create(
                {
                    "name": "Furnizori - facturi nesosite",
                    "code": "408000",
                    "user_type_id": account_type_current_liabilities.id,
                    "reconcile": False,
                }
            )
        cls.env.user.company_id.property_stock_picking_payable_account_id = cls.stock_picking_payable_account_id

        cls.stock_picking_receivable_account_id = cls.env.user.company_id.property_stock_picking_receivable_account_id
        if not cls.stock_picking_receivable_account_id:
            cls.stock_picking_receivable_account_id = cls.env["account.account"].search([("code", "=", "418000")])
        if not cls.stock_picking_receivable_account_id:
            cls.stock_picking_receivable_account_id = cls.env["account.account"].create(
                {
                    "name": "Clienti  - facturi nesosite",
                    "code": "418000",
                    "user_type_id": account_type_cur.id,
                    "reconcile": False,
                }
            )
        cls.env.user.company_id.property_stock_picking_receivable_account_id = cls.stock_picking_receivable_account_id

        stock_journal = cls.env["account.journal"].search([("code", "=", "STJ")])
        if not stock_journal:
            stock_journal = cls.env["account.journal"].create(
                {"name": "Stock Journal", "code": "STJ", "type": "general"}
            )

        category_value = {
            "name": "TEST Marfa",
            "property_cost_method": "fifo",
            "property_valuation": "real_time",
            "property_account_creditor_price_difference_categ": cls.account_difference.id,
            "property_account_income_categ_id": cls.account_income.id,
            "property_account_expense_categ_id": cls.account_expense.id,
            "property_stock_account_input_categ_id": cls.account_input.id,
            "property_stock_account_output_categ_id": cls.account_output.id,
            "property_stock_valuation_account_id": cls.account_valuation.id,
            "property_stock_journal": stock_journal.id,
        }

        domain = [("name", "=", "l10n_ro_stock_account"), ("state", "=", "installed")]
        l10n_ro_stock_account_module = cls.env["ir.module.module"].search(domain)
        if l10n_ro_stock_account_module:
            category_value.update(
                {
                    "property_stock_account_input_categ_id": cls.account_valuation.id,
                    "property_stock_account_output_categ_id": cls.account_valuation.id,
                }
            )

        cls.category = cls.env["product.category"].search([("name", "=", "TEST Marfa")])
        if not cls.category:
            cls.category = cls.env["product.category"].create(category_value)
        else:
            cls.category.write(category_value)

        cls.price_p1 = 50.0
        cls.price_p2 = round(random.random() * 100, 2)
        cls.list_price_p1 = 70.0
        cls.list_price_p2 = round(cls.price_p2 + random.random() * 50, 2)

        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
                "categ_id": cls.category.id,
                "invoice_policy": "delivery",
                "purchase_method": "receive",
                "list_price": cls.list_price_p1,
                "standard_price": cls.price_p1,
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Product B",
                "type": "product",
                "purchase_method": "receive",
                "categ_id": cls.category.id,
                "invoice_policy": "delivery",
                "list_price": cls.list_price_p2,
                "standard_price": cls.price_p2,
            }
        )

        cls.vendor = cls.env["res.partner"].search([("name", "=", "TEST Vendor")], limit=1)
        if not cls.vendor:
            cls.vendor = cls.env["res.partner"].create({"name": "TEST Vendor"})

        cls.client = cls.env["res.partner"].search([("name", "=", "TEST Client")], limit=1)
        if not cls.client:
            cls.client = cls.env["res.partner"].create({"name": "TEST Client"})

        cls.diff_p1 = 1
        cls.diff_p2 = -1

        # cantitatea din PO
        cls.qty_po_p1 = 20.0
        cls.qty_po_p2 = 20.00

        # cantitata din SO
        cls.qty_so_p1 = 2.0
        cls.qty_so_p2 = 2.0

        cls.val_p1_i = round(cls.qty_po_p1 * cls.price_p1, 2)
        cls.val_p2_i = round(cls.qty_po_p2 * cls.price_p2, 2)
        cls.val_p1_f = round(cls.qty_po_p1 * (cls.price_p1 + cls.diff_p1), 2)
        cls.val_p2_f = round(cls.qty_po_p2 * (cls.price_p2 + cls.diff_p2), 2)

        # valoarea descarcari de gestiune
        cls.val_stock_out_so_p1 = round(cls.qty_so_p1 * cls.price_p1, 2)
        cls.val_stock_out_so_p2 = round(cls.qty_so_p2 * cls.price_p2, 2)

        # valoarea vanzarii
        cls.val_so_p1 = round(cls.qty_so_p1 * cls.list_price_p1, 2)
        cls.val_so_p2 = round(cls.qty_so_p2 * cls.list_price_p2, 2)

        cls.val_p1_store = cls.qty_po_p1 * cls.list_price_p1
        cls.val_p2_store = cls.qty_po_p2 * cls.list_price_p2

        cls.tva_p1 = cls.val_p1_store * 0.19
        cls.tva_p2 = cls.val_p2_store * 0.19
        cls.val_p1_store = round(cls.val_p1_store + cls.tva_p1, 2)
        cls.val_p2_store = round(cls.val_p2_store + cls.tva_p2, 2)

        cls.adaos_p1 = round(cls.val_p1_store - cls.val_p1_i, 2)
        cls.adaos_p2 = round(cls.val_p2_store - cls.val_p2_i, 2)

        cls.adaos_p1_f = round(cls.val_p1_store - cls.val_p1_f, 2)
        cls.adaos_p2_f = round(cls.val_p2_store - cls.val_p2_f, 2)

        picking_type_in = cls.env.ref("stock.picking_type_in")
        location = picking_type_in.default_location_dest_id

        cls.location_warehouse = location.copy({"merchandise_type": "warehouse", "name": "TEST warehouse"})
        cls.picking_type_in_warehouse = picking_type_in.copy(
            {"default_location_dest_id": cls.location_warehouse.id, "name": "TEST Receptie in Depozit"}
        )

        cls.location_store = location.copy({"merchandise_type": "store", "name": "TEST store"})
        cls.picking_type_in_store = picking_type_in.copy(
            {"default_location_dest_id": cls.location_store.id, "name": "TEST Receptie in magazin"}
        )

        cls.env.user.company_id.anglo_saxon_accounting = True

    def create_po(self, notice=False, picking_type_in=None):

        if not picking_type_in:
            picking_type_in = self.picking_type_in_warehouse

        po = Form(self.env["purchase.order"])
        po.partner_id = self.vendor
        po.picking_type_id = picking_type_in

        with po.order_line.new() as po_line:
            po_line.product_id = self.product_1
            po_line.product_qty = self.qty_po_p1
            po_line.price_unit = self.price_p1

        with po.order_line.new() as po_line:
            po_line.product_id = self.product_2
            po_line.product_qty = self.qty_po_p2
            po_line.price_unit = self.price_p2

        po = po.save()
        po.button_confirm()
        self.picking = po.picking_ids[0]
        self.picking.write({"notice": notice})
        for move_line in self.picking.move_line_ids:
            if move_line.product_id == self.product_1:
                move_line.write({"qty_done": self.qty_po_p1})
            if move_line.product_id == self.product_2:
                move_line.write({"qty_done": self.qty_po_p2})

        self.picking.button_validate()

        self.po = po
        return po

    def create_invoice(self, diff_p1=0, diff_p2=0):
        invoice = Form(self.env["account.move"].with_context(default_type="in_invoice"))
        invoice.partner_id = self.vendor
        invoice.purchase_id = self.po

        with invoice.invoice_line_ids.edit(0) as line_form:
            line_form.price_unit += diff_p1
        with invoice.invoice_line_ids.edit(1) as line_form:
            line_form.price_unit += diff_p2

        invoice = invoice.save()

        invoice.post()

    def make_puchase(self):
        self.create_po()
        self.create_invoice()

    def check_stock_valuation(self, val_p1, val_p2):
        val_p1 = round(val_p1, 2)
        val_p2 = round(val_p2, 2)
        domain = [("product_id", "in", [self.product_1.id, self.product_2.id])]
        valuations = self.env["stock.valuation.layer"].read_group(domain, ["value:sum", "quantity:sum"], ["product_id"])

        for valuation in valuations:
            val = round(valuation["value"], 2)
            if valuation["product_id"][0] == self.product_1.id:
                print("Check stoc P1 ", val, "=", val_p1)
                self.assertEqual(val, val_p1)
            if valuation["product_id"][0] == self.product_2.id:
                print("Check stoc P2", val, "=", val_p2)
                self.assertEqual(val, val_p2)

    def check_account_valuation(self, val_p1, val_p2, account=None):
        val_p1 = round(val_p1, 2)
        val_p2 = round(val_p2, 2)
        if not account:
            account = self.account_valuation

        domain = [("product_id", "in", [self.product_1.id, self.product_2.id]), ("account_id", "=", account.id)]
        account_valuations = self.env["account.move.line"].read_group(
            domain, ["debit:sum", "credit:sum", "quantity:sum"], ["product_id"]
        )

        for valuation in account_valuations:
            val = round(valuation["debit"] - valuation["credit"], 2)
            if valuation["product_id"][0] == self.product_1.id:
                print("Check ", val, "=", val_p1)
                self.assertEqual(val, val_p1)
            if valuation["product_id"][0] == self.product_2.id:
                print("Check ", val, "=", val_p2)
                self.assertEqual(val, val_p2)

    def check_account_diff(self, val_p1, val_p2):
        self.check_account_valuation(val_p1, val_p2, self.account_difference)
