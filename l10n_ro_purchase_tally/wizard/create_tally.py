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

class CreatePurchaseTally(models.TransientModel):
    _name = "purchase_tally.tally"
    _description = "Wizard for creating Purchase Tally"

    partner_id = fields.Many2one('res.partner')
    partner_name = fields.Char(string='Nume')
    partner_surname = fields.Char(string='Prenume')
    partner_address = fields.Char(string='Adresa')
    partner_ci = fields.Char(string="Serie si nr CI")

    tally_lines = fields.One2many('purchase_tally.tally.item','purchase_tally_id')

    @api.multi
    def create_tally(self):
        for line in self.tally_lines:
            if line.price_subtotal <= 0:
                raise UserError(_('Nu se pot achizitiona produse cu valoare2 0!'))
        pass


class PurchaseTallyItems(models.TransientModel):
    _name = 'purchase_tally.tally.item'
    _description = "Purchase Tally Item"

    sequence = fields.Integer(string='Sequence', default=10)
    purchase_tally_id = fields.Many2one('purchase_tally.tally')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    name = fields.Char(string='Description')
    product_qty = fields.Float(string="Qty", digits=dp.get_precision('Product Unit of Measure'))
    product_uom = fields.Many2one('product.uom', string='Product Unit of Measure', required=True)
    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Product Price'))
    price_subtotal = fields.Float(compute='_compute_amount', string='Valoare')

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id

    @api.depends('product_qty', 'price_unit')
    def _compute_amount(self):
        for line in self:
            line.update({
                'price_subtotal': line.product_qty*line.price_unit,
            })