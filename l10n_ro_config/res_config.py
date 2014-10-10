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

import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp

class l10n_ro_config_settings(models.Model):
    _name = 'l10n.ro.config.settings'
    _inherit = 'res.config.settings'

    company_id = fields.Many2one('res.company', 'Company', change_default=True,
        default=lambda self: self.env['res.company']._company_default_get('l10n.ro.config.settings'))
    has_default_company = fields.Boolean('Has default company', readonly=True, change_default=True,
        default=lambda self: bool(self.env['res.company'].search_count([]) == 1))
    module_account_storno = fields.Boolean('Storno Accounting',
            help='This allows you to manage the storno behaviour in accounting.')
    module_account_vat_on_payment = fields.Boolean('Vat on Payment Accounting',
            help='This allows you to manage the vat on payment behaviour in accounting.')
    module_l10n_ro_asset = fields.Boolean('Romanian Asset',
            help='This allows you to manage the Romanian adaptation for assets, including:\n'
                 'Split assets in fixed assets and services (financials).\n'
                 'Fixed assets will be created / sold from stock moves, services assets from invoices,\n'
                 'also include history of creation of the asset.\n'
                 'Method of reevaluation of assets.'
                 'Import of the Chart of Asset Categories according with the legislation')
    module_l10n_ro_stock = fields.Boolean('Romanian Stock',
            help='This allows you to manage the Romanian adaptation for stock, including:\n'
                 'New stock accounts on location to allow moving entry in accounting based on the stock move.\n'
                 'The account entry will be generated from stock move instead of stock quant, link with the generated \n'
                 'account move lines on the picking\n'
                 'Methods of usage giving and consumption'
                 'Inventory account move lines...')
    module_l10n_ro_zip = fields.Boolean('Romanian Cities',
            help='This allows you to manage the Romanian zipcodes on addreses:\n'
                 'The addres fields will be replaced by one location field including city, state, country, zip.')
    module_currency_rate_update = fields.Boolean('Currency Rate Update',
            help='This allows you to manage the update of currency rate based on different provider, use BNR site.\n')
    module_l10n_ro_invoice_line_not_deductible = fields.Boolean('Not Deductible Invoice Line',
            help='This allows you to manage not deductible supplier invoice line.\n')
    module_l10n_ro_account_constrains = fields.Boolean('Account Constrains',
            help='This allows will remove the constrains related to account journal, account with secondary currency.\n')
    module_l10n_ro_account_bank_statement = fields.Boolean('Bank Statement Invoices',
            help='This allows you to manage imports in bank statement line of the invoices only.\n')
    module_l10n_ro_account_voucher_cash = fields.Boolean('Voucher to Cash Statement',
            help='This allows you to directly input in cash statement payments/receipts from cash journals.\n')
    module_l10n_ro_account_voucher_currency_update = fields.Boolean('Currency Difference on Partial Payments/Receipts',
            help='This allows you to manage recors currency difference amounts on partial payments/receipts.\n')
    property_undeductible_account_id = fields.Many2one('account.account',
            related='company_id.property_undeductible_account_id',
            type="many2one",
            relation='account.account',
            string="Undeductible Account",
            domain="[('type', '=', 'other')]", change_default=True,
            default=lambda self: self.env['account.account'].search([('code','ilike','635')]),
            help="This account will be used as the undeductible account in account move line")
    property_stock_picking_payable_account_id = fields.Many2one('account.account',
            related='company_id.property_stock_picking_payable_account_id',
            string="Picking Account Payable",
            domain="[('type', '=', 'payable')]", change_default=True,
            default=lambda self: self.env['account.account'].search([('code','ilike','408')]),
            help="This account will be used as the payable account for the current partner on stock picking notice")
    property_stock_picking_receivable_account_id = fields.Many2one('account.account',
            related='company_id.property_stock_picking_receivable_account_id',
            string="Picking Account Receivable",
            domain="[('type', '=', 'receivable')]", change_default=True,
            default=lambda self: self.env['account.account'].search([('code','ilike','418')]),
            help="This account will be used as the receivable account for the current partner on stock picking notice")
    property_stock_usage_giving_account_id = fields.Many2one('account.account',
            related='company_id.property_stock_usage_giving_account_id',
            string="Usage Giving Account",
            domain="[('type', '=', 'other')]", change_default=True,
            default=lambda self: self.env['account.account'].search([('code','ilike','8035')]),
            help="This account will be used as the usage giving account in account move line")
    property_asset_reevaluation_account_id = fields.Many2one('account.account',
            related='company_id.property_asset_reevaluation_account_id',
            string="Asset Reevaluation Account",
            domain="[('type', '=', 'other')]", change_default=True,
            default=lambda self: self.env['account.account'].search([('code','ilike','105')]),
            help="This account will be used as the reevaluation asset account.")
    property_customer_advance_account_id = fields.Many2one('account.account',
            related='company_id.property_customer_advance_account_id',
            string="Customer Advance Account",
            domain="[('type', '=', 'receivable')]", change_default=True,
            default=lambda self: self.env['account.account'].search([('code','ilike','419')]),
            help="This account will be used as the customer advance account for the current partner on vouchers.")
    property_supplier_advance_account_id = fields.Many2one('account.account',
            related='company_id.property_supplier_advance_account_id',
            string="Supplier Advance Account",
            domain="[('type', '=', 'payable')]", change_default=True,
            default=lambda self: self.env['account.account'].search([('code','ilike','4091')]),
            help="This account will be used as the supplier advance account for the current partner on vouchers.")
    
