# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Business Applications
#    Copyright (C) 2014-2015 Odoo S.A. <http://www.odoo.com>
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models
from odoo.tools.sql import drop_view_if_exists

class account_invoice(models.Model):
    _inherit = "account.invoice"


    #exista incoterm_id in 12
    # incoterm_id = fields.Many2one(
    #         'account.incoterms', 'Incoterm',
    #         help="International Commercial Terms are a series of predefined commercial terms "
    #              "used in international transactions.")
    intrastat_transaction_id = fields.Many2one(
            'l10n_ro_intrastat.transaction', 'Intrastat Transaction Type',
            help="Intrastat nature of transaction")
    transport_mode_id = fields.Many2one(
            'l10n_ro_intrastat.transport_mode', 'Intrastat Transport Mode')
    intrastat_country_id = fields.Many2one(
            'res.country', 'Intrastat Country',
            help='Intrastat country, delivery for sales, origin for purchases',
            domain=[('intrastat','=',True)])





class intrastat_transaction(models.Model):
    _name = 'l10n_ro_intrastat.transaction'
    _rec_name = 'description'

    code = fields.Char('Code', required=True, readonly=True)
    parent_id = fields.Many2one('l10n_ro_intrastat.transaction', 'Parent Code', readonly=True)
    description = fields.Text('Description', readonly=True)


    _sql_constraints = [
        ('l10n_ro_intrastat_trcodeunique', 'UNIQUE (code)', 'Code must be unique.'),
    ]


class intrastat_transport_mode(models.Model):
    _name = 'l10n_ro_intrastat.transport_mode'

    code = fields.Char('Code', required=True, readonly=True)
    name = fields.Char('Description', readonly=True)


    _sql_constraints = [
        ('l10n_ro_intrastat_trmodecodeunique', 'UNIQUE (code)', 'Code must be unique.'),
    ]



#NU exista in 12.

# class purchase_order(models.Model):
#     _inherit = "purchase.order"
#
#     def _prepare_invoice(self, cr, uid, order, line_ids, context=None):
#         """
#         copy incoterm from purchase order to invoice
#         """
#         invoice = super(purchase_order, self)._prepare_invoice(  cr, uid, order, line_ids, context=context)
#         if order.incoterm_id:
#             invoice['incoterm_id'] = order.incoterm_id.id
#         #Try to determine products origin
#         if order.partner_id.country_id:
#             #It comes from supplier
#             invoice['intrastat_country_id'] = order.partner_id.country_id.id
#
#         return invoice






class res_company(models.Model):
    _inherit = "res.company"


    intrastat_transaction_id = fields.Many2one(
            'l10n_ro_intrastat.transaction', 'Intrastat Transaction Type',
            help="Intrastat nature of transaction")
                       
    transport_mode_id = fields.Many2one('l10n_ro_intrastat.transport_mode',
                                             'Default transport mode')
    incoterm_id = fields.Many2one('account.incoterms', 'Default incoterm for Intrastat',
                                       help="International Commercial Terms are a series of "
                                            "predefined commercial terms used in international "
                                            "transactions.")



class sale_order(models.Model):
    _inherit = "sale.order"




    def _prepare_invoice(self):
        invoice_vals = super(sale_order, self)._prepare_invoice()

        if self.incoterm:
            invoice_vals['incoterm_id'] = self.incoterm.id
        # Guess products destination
        if self.partner_shipping_id.country_id:
            invoice_vals['intrastat_country_id'] = self.partner_shipping_id.country_id.id
        elif self.partner_id.country_id:
            invoice_vals['intrastat_country_id'] = self.partner_id.country_id.id
        elif self.partner_invoice_id.country_id:
            invoice_vals['intrastat_country_id'] = self.partner_invoice_id.country_id.id


        return invoice_vals




