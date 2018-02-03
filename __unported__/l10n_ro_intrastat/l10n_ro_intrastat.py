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

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo import tools

class account_invoice(models.Model):
    _inherit = "account.invoice"
 
    incoterm_id = fields.Many2one( 'stock.incoterms', 'Incoterm',
            help="International Commercial Terms are a series of predefined commercial terms "
                 "used in international transactions.")
    intrastat_transaction_id = fields.Many2one( 'l10n_ro_intrastat.transaction', 'Intrastat Transaction Type',
            help="Intrastat nature of transaction")
    transport_mode_id = fields.Many2one( 'l10n_ro_intrastat.transport_mode', 'Intrastat Transport Mode')
    intrastat_country_id = fields.Many2one( 'res.country', 'Intrastat Country',
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
        ('l10n_ro_intrastat_trmodecodeunique', 'UNIQUE (code)', 'Code must be unique.')
    ]


class product_category(models.Model):
    _name = "product.category"
    _inherit = "product.category"

 

    intrastat_id = fields.Many2one('report.intrastat.code', string='Intrastat Code')

    @api.multi
    def get_intrastat_recursively(self):
        """ Recursively search in categories to find an intrastat code id
        """
        res = None
        if self.intrastat_id:
            res = self.intrastat_id.id
        elif self.parent_id:
            res = self.parent_id.get_intrastat_recursively()
        return res


class product_product(models.Model):
    _name = "product.product"
    _inherit = "product.product"

    @api.multi
    def get_intrastat_recursively(self):
        """ Recursively search in categories to find an intrastat code id
        """
        res = None
        if self.intrastat_id:
            res = self.intrastat_id.id
        elif self.categ_id:
            res = self.categ_id.get_intrastat_recursively()
        return res


class purchase_order(models.Model):
    _inherit = "purchase.order"


    def _prepare_invoice(self):
        """
        copy incoterm from purchase order to invoice
        """
        invoice = super(PurchaseOrder, self)._prepare_invoice()
        if self.incoterm_id:
            invoice['incoterm_id'] = self.incoterm_id.id
        # Try to determine products origin
        if self.partner_id.country_id:
            # It comes from vendor
            invoice['intrastat_country_id'] = self.partner_id.country_id.id
        return invoice


class report_intrastat_code(models.Model):
    _inherit = "report.intrastat.code"
    
    description = fields.Text(string='Description', translate=True)
 


class res_company(models.Model):
    _inherit = "res.company"
    

    intrastat_transaction_id = fields.Many2one(
            'l10n_ro_intrastat.transaction', 'Intrastat Transaction Type',
            help="Intrastat nature of transaction")
                       
    transport_mode_id = fields.Many2one('l10n_ro_intrastat.transport_mode',    'Default transport mode')
    incoterm_id = fields.Many2one('stock.incoterms', 'Default incoterm for Intrastat',
                                       help="International Commercial Terms are a series of "
                                            "predefined commercial terms used in international "
                                            "transactions.")
 


class SaleOrder(models.Model):
    _inherit = "sale.order"


    def _prepare_invoice(self):
        """
        copy incoterm from sale order to invoice
        """
        invoice = super(SaleOrder, self)._prepare_invoice()
        if self.incoterm:
            invoice['incoterm_id'] = self.incoterm.id
        # Guess products destination
        if self.partner_shipping_id.country_id:
            invoice['intrastat_country_id'] = self.partner_shipping_id.country_id.id
        elif self.partner_id.country_id:
            invoice['intrastat_country_id'] = self.partner_id.country_id.id
        elif self.partner_invoice_id.country_id:
            invoice['intrastat_country_id'] = self.partner_invoice_id.country_id.id
        return invoice


class report_intrastat_code(models.Model):
    _inherit = "report.intrastat.code"
 

    suppl_unit_code = fields.Char(string='SupplUnitCode')



