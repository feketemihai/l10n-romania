# Copyright (C) 2020 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import random
from odoo.tests import Form
from .common import TestStockCommon

# Generare note contabile la achizitie

class TestStockPurchase(TestStockCommon):


    def test_nir_with_invoice(self):
        """
            Receptie produse in depozit in baza facturii
             - in stoc valoarea de achiztie
             - in contabilitate valoarea de achiztie
             - in diferente de pret zero
             - in TVA neexigibilă zero
        """
        po = self.create_po()

        self.check_stock_valuation(self.val_p1_i, self.val_p2_i)

        # in contabilitate trebuie sa fie zero pentru ca la receptie nu trebuie generata nota cantabila
        self.check_account_valuation(0, 0)

        self.create_invoice()

        self.check_stock_valuation(self.val_p1_i, self.val_p2_i)

        self.check_account_valuation(self.val_p1_i, self.val_p2_i)

        # verificare inregistrare diferenta de pret
        self.check_account_diff(0, 0)


    def test_nir_with_invoice_and_diff(self):
        """
         Receptie produse in baza facturii cu inregistrare diferente dintre comanda de achizitie si factura
         Diferentele trebuie sa fie inregitrate in contul de stoc
             - in stoc valoarea de achiztie din factura
             - in contabilitate valoarea de achiztie din factura
             - in diferente de pret zero
             - in TVA neexigibilă zero
        """
        po = self.create_po()

        self.check_stock_valuation(self.qty_p1 * self.price_p1, self.qty_p2 * self.price_p2)
        # in contabilitate trebuie sa fie zero pentru ca la receptie nu trebuie generata nota cantabila
        self.check_account_valuation(0, 0)

        self.create_invoice(self.diff_p1, self.diff_p2)

        # in stocul  are valoarea cu diferenta de pret inregistrata
        self.check_stock_valuation(self.val_p1_f, self.val_p2_f)

        # in contabilitate stocul are acceasi valoare
        self.check_account_valuation(self.val_p1_f, self.val_p2_f)

        # verificare inregistrare diferenta de pret
        self.check_account_diff(0, 0)



    def test_nir_with_notice_and_invoice(self):
        """
            Receptie produse pe baza de aviz si inregistare ulterioara a facturii
        """
        po = self.create_po(notice=True)

        self.check_stock_valuation(self.val_p1_i, self.val_p2_i)
        self.check_account_valuation(self.val_p1_i, self.val_p2_i)

        self.create_invoice()

        self.check_stock_valuation(self.val_p1_i, self.val_p2_i)
        self.check_account_valuation(self.val_p1_i, self.val_p2_i)




    def test_nir_with_notice_invoice_and_diff(self):
        """
         Receptie produse pe baza de aviz si inregistare ulterioara a facturii
         cu inregistrare diferente dintre comanda de achzitie si factura
         Diferentele trebuie sa fie inregitrate in contul de diferente de stoc
        """
        po = self.create_po(notice=True)

        # in stoc produsele sunt la valoarea de achizitie
        self.check_stock_valuation(self.val_p1_i, self.val_p2_i)

        self.check_account_valuation(self.val_p1_i, self.val_p2_i)

        self.create_invoice(self.diff_p1, self.diff_p2)

        # in stoc produsele sunt la valoarea de achizitie
        self.check_stock_valuation(self.val_p1_i, self.val_p2_i)

        # in contabilitate stocul are acceasi valoare
        self.check_account_valuation(self.val_p1_i, self.val_p2_i)

        # verificare inregistrare diferenta de pret
        self.check_account_diff(self.val_p1_f - self.val_p1_i, self.val_p2_f - self.val_p2_i)

