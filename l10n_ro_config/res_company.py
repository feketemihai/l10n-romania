# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Fekete Mihai <mihai.fekete@forbiom.eu>
#    Copyright (C) 2014 FOREST AND BIOMASS SERVICES ROMANIA SA (http://www.forbiom.eu).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID, api

class res_company(osv.osv):
    _inherit = 'res.company'
    
    _columns = {
        'property_stock_usage_giving_account_id': fields.property(
            type='many2one',
            relation='account.account',
            string="Usage Giving Account",
            domain="[('type', '=', 'other')]",
            help="This account will be used as the undeductible account foraccount move line."),
        'property_undeductible_account_id': fields.property(
            type='many2one',
            relation='account.account',
            string="Undeductible Account",
            domain="[('type', '=', 'other')]",
            help="This account will be used as the undeductible account for account move line."),
        'property_stock_picking_payable_account_id': fields.property(
            type='many2one',
            relation='account.account',
            string="Picking Account Payable",
            domain="[('type', '=', 'payable')]",
            help="This account will be used as the payable account for the current partner on stock picking notice."),
        'property_stock_picking_receivable_account_id': fields.property(
            type='many2one',
            relation='account.account',
            string="Picking Account Receivable",
            domain="[('type', '=', 'receivable')]",
            help="This account will be used as the receivable account for the current partner on stock picking notice."),
        'property_asset_reevaluation_account_id': fields.property(
            type='many2one',
            relation='account.account',
            string="Asset Reevaluation Account",
            domain="[('type', '=', 'other')]",
            help="This account will be used as the reevaluation asset account."),
        'property_customer_advance_account_id':  fields.property(
            type='many2one',
            relation='account.account',
            string="Customer Advance Account",
            domain="[('type', '=', 'receivable')]",
            help="This account will be used as the customer advance account for the current partner on vouchers."),
        'property_supplier_advance_account_id': fields.property(
            type='many2one',
            relation='account.account',
            string="Supplier Advance Account",
            domain="[('type', '=', 'payable')]",
            help="This account will be used as the supplier advance account for the current partner on vouchers."),        
    }
