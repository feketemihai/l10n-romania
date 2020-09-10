# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2018 Terrabit Solutions. All rights reserved.
#    @author Dorin Hongu/Dan Stoica
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime

# Adaugare camp la purchase_order pentru diferentiere
class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    is_tally = fields.Boolean("Is tally")


class CreatePurchaseTally(models.TransientModel):
    _name = "purchase_tally.tally"
    _description = "Wizard for creating Purchase Tally"

    partner_id = fields.Many2one("res.partner")
    partner_name = fields.Char(string="Nume")
    partner_surname = fields.Char(string="Prenume")
    partner_address = fields.Char(string="Adresa")
    partner_ci = fields.Char(string="Serie si nr CI")
    picking_type = fields.Many2one("stock.picking.type")
    tally_lines = fields.One2many("purchase_tally.tally.item", "purchase_tally_id")

    def wizard_close(self):
        return {"type": "ir.actions.act_window_close"}

    @api.multi
    def create_tally(self):
        # if self.tally_lines:
        for line in self.tally_lines:  # verificare linii
            if line.price_subtotal <= 0:
                raise UserError(_("Nu se pot achizitiona produse cu valoare 0!"))

        # Cautare/creare partener
        partner = self.env["res.partner"].with_context(active_test=False).search([("id_nr", "=", self.partner_ci)])
        if not partner:
            values = {
                "name": self.partner_name + " " + self.partner_surname,
                "street": self.partner_address,
                "id_nr": self.partner_ci,
                "company_type": "person",
                "email": "@",
                "supplier": True,
                "customer": False,
                "active": False,
            }
            partner = self.env["res.partner"].create(values)

        # Creare comanda achizitie
        values = {
            "is_tally": True,
            "partner_id": partner.id,
            "date_planned": datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
            "picking_type_id": self.picking_type.id,
            "partner_ref": self.env["ir.sequence"].next_by_code("purchase_tally.tally"),
        }
        purchase_order = self.env["purchase.order"].create(values)

        # Creare linii comanda de achizitie
        for line in self.tally_lines:
            values = {
                "order_id": purchase_order.id,
                "product_id": line.product_id.id,
                "name": line.product_id.name,
                "product_qty": line.product_qty,
                "price_unit": line.price_unit,
                "product_uom": line.product_uom.id,
                "date_planned": datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
            }
            self.env["purchase.order.line"].create(values)

        # Confirmare comanda achizitie
        purchase_order.button_confirm()

        # Confirmare pickings
        for picking in purchase_order.picking_ids:
            for move_line in picking.move_lines:
                move_line.quantity_done = move_line.product_uom_qty
            picking.button_validate()

        # Setare comanda achizitie pe nimic de facturat
        purchase_order.write({"invoice_status": "no"})

        # Print pickings
        res = self.env.ref("l10n_ro_purchase_tally.action_report_tally").report_action(purchase_order.picking_ids)

        # TODO: Close wizard

        return res


class PurchaseTallyItems(models.TransientModel):
    _name = "purchase_tally.tally.item"
    _description = "Purchase Tally Item"

    sequence = fields.Integer(string="Sequence", default=10)
    purchase_tally_id = fields.Many2one("purchase_tally.tally")
    product_id = fields.Many2one("product.product", string="Product", required=True)
    name = fields.Char(string="Description")
    product_qty = fields.Float(string="Qty", digits=dp.get_precision("Product Unit of Measure"))
    product_uom = fields.Many2one("uom.uom", string="UoM", required=True)
    price_unit = fields.Float(string="Unit Price", required=True, digits=dp.get_precision("Product Price"))
    price_subtotal = fields.Float(compute="_compute_amount", string="Valoare")

    @api.onchange("product_id")
    def onchange_product_id(self):
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id

    @api.depends("product_qty", "price_unit")
    def _compute_amount(self):
        for line in self:
            line.update(
                {"price_subtotal": line.product_qty * line.price_unit,}
            )
