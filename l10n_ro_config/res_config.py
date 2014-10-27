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

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

import csv
import os

class l10n_ro_config_settings(models.TransientModel):
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
    module_l10n_ro_account_report = fields.Boolean('Romania Accounting Reports',
            help='This allows you to print reports according to legislation like: Sale/Purchase Journals, Trial Balance, D394..\n')
    module_l10n_ro_account_period_close = fields.Boolean('Romania Account Period Close',
            help='This allows you to close accounts on periods based on templates: Income, Expense, VAT...\n')
    property_undeductible_account_id = fields.Many2one('account.account', related='company_id.property_undeductible_account_id',
            string="Undeductible Account",
            domain="[('type', '=', 'other'),('company_id','=',company_id)]",
            help="This account will be used as the undeductible account in account move line")
    property_stock_picking_payable_account_id = fields.Many2one('account.account', related='company_id.property_stock_picking_payable_account_id',
            string="Picking Account Payable",
            domain="[('type', '=', 'payable'),('company_id','=',company_id)]",
            help="This account will be used as the payable account for the current partner on stock picking notice")
    property_stock_picking_receivable_account_id = fields.Many2one('account.account', related='company_id.property_stock_picking_receivable_account_id',
            string="Picking Account Receivable",
            domain="[('type', '=', 'receivable'),('company_id','=',company_id)]",
            help="This account will be used as the receivable account for the current partner on stock picking notice")
    property_stock_usage_giving_account_id = fields.Many2one('account.account', related='company_id.property_stock_usage_giving_account_id',
            string="Usage Giving Account",
            domain="[('type', '=', 'other'),('company_id','=',company_id)]",
            help="This account will be used as the usage giving account in account move line")
    property_asset_reevaluation_account_id = fields.Many2one('account.account', related='company_id.property_asset_reevaluation_account_id',
            string="Asset Reevaluation Account",
            domain="[('type', '=', 'other'),('company_id','=',company_id)]",
            help="This account will be used as the reevaluation asset account.")
    property_customer_advance_account_id = fields.Many2one('account.account', related='company_id.property_customer_advance_account_id',
            string="Customer Advance Account",
            domain="[('type', '=', 'receivable'),('company_id','=',company_id)]",
            help="This account will be used as the customer advance account for the current partner on vouchers.")
    property_supplier_advance_account_id = fields.Many2one('account.account', related='company_id.property_supplier_advance_account_id',
            string="Supplier Advance Account",
            domain="[('type', '=', 'payable'),('company_id','=',company_id)]",
            help="This account will be used as the supplier advance account for the current partner on vouchers.")
    asset_category_chart_installed = fields.Boolean('Install Chart of Asset Category', related='company_id.asset_category_chart_installed')
    bank_statement_template_installed = fields.Boolean('Load Bank Statement Templates', related='company_id.bank_statement_template_installed')
    
    @api.model
    def create(self, values):
        id = super(l10n_ro_config_settings, self).create(values)
        # Hack: to avoid some nasty bug, related fields are not written upon record creation.
        # Hence we write on those fields here.
        vals = {}
        for fname, field in self._columns.iteritems():
            if isinstance(field, fields.Many2one) and fname in values:
                vals[fname] = values[fname]
        self.write(vals)
        return id

    @api.multi
    def onchange_company_id(self, company_id):
        # update related fields
        values = {}
        if company_id:
            company = self.env['res.company'].browse(company_id)
            # update romanian configuration accounts
            values.update({
                'property_undeductible_account_id' : company.property_undeductible_account_id and company.property_undeductible_account_id.id or False,
                'property_stock_picking_payable_account_id' : company.property_stock_picking_payable_account_id and company.property_stock_picking_payable_account_id.id or False,
                'property_stock_picking_receivable_account_id' : company.property_stock_picking_receivable_account_id and company.property_stock_picking_receivable_account_id.id or False,
                'property_stock_usage_giving_account_id' : company.property_stock_usage_giving_account_id and company.property_stock_usage_giving_account_id.id or False,
                'property_asset_reevaluation_account_id' : company.property_asset_reevaluation_account_id and company.property_asset_reevaluation_account_id.id or False,
                'property_customer_advance_account_id' : company.property_customer_advance_account_id and company.property_customer_advance_account_id.id or False,
                'property_supplier_advance_account_id' : company.property_supplier_advance_account_id and company.property_supplier_advance_account_id.id or False,
                'asset_category_chart_installed': company.asset_category_chart_installed,
                'bank_statement_template_installed': company.bank_statement_template_installed,
            })
        return {'value': values}
    
    @api.multi
    def execute(self):
        res = super(l10n_ro_config_settings, self).execute()
        # Load Chart of Asset Category if not installed previously
        categ_obj = self.env['account.asset.category']
        account_obj = self.env['account.account']
        installed = self.env['ir.module.module'].search([('name','=','l10n_ro_asset'),('state','=','installed')])
        if installed:
            wiz = self[0]
            if wiz.asset_category_chart_installed:
                asset_categ = categ_obj.search([('name','=','Catalog Mijloace Fixe'),('company_id','=',wiz.company_id.id)])
                if not asset_categ:
                    journal_obj = self.env['account.journal']
                    journal_id = journal_obj.search([('code','=','AMORT'),('company_id','=',wiz.company_id.id)])
                    # Search for Amortization Journal on company, if doesn't exist create it.
                    if not journal_id:
                        default_account_id = account_obj.search([('code','=','681100'),('company_id','=',wiz.company_id.id)])
                        if default_account_id:
                            journal_id = journal_obj.create({"name": 'Jurnal amortizare', "code": 'AMORT',
                                                        "type": 'general', "user_id": self.env.user.id,
                                                        "default_credit_account_id": default_account_id[0].id,
                                                        "default_debit_account_id": default_account_id[0].id,
                                                        "company_id" : wiz.company_id.id})
                    journal_id = journal_id[0].id
                    # Search for inventory sequence for fixed asset, if doesn't exist create it
                    inv_sequence_id = self.env['ir.sequence'].search([('name','=','Inventar Mijloace Fixe'),('company_id','=',wiz.company_id.id)])
                    if not inv_sequence_id:
                        inv_sequence_id = self.env['ir.sequence'].create({"name": 'Inventar Mijloace Fixe',
                                                                        "padding": 6, "implementation": 'no_gap',
                                                                        "number_next": 1, "number_increment": 1,
                                                                        "prefix": 'INV/', "company_id" : wiz.company_id.id})
                    inv_sequence_id = inv_sequence_id[0].id
                    script_dir = os.path.dirname(os.getcwd())
                    rel_path = str(script_dir) + "/l10n-romania/l10n_ro_config/data/categoriiactive.csv"
                    f = open(rel_path, 'rb')
                    try:
                     
                        categorii = csv.DictReader(f)
                    # id,parent_id,code,name,type,asset_type,method_number_min,method_number,account_asset_id,account_depreciation_id,account_expense_id,account_income_id,method,method_time,method_period
                        for row in categorii:
                            categ = categ_obj.search([('code','=',row['code']), ('company_id','=', wiz.company_id.id)])
                            if not categ:
                                if row['parent_code']:
                                    parent_category_id = categ_obj.search([('code','=',row['parent_code']),('company_id','=',wiz.company_id.id)])
                                    if parent_category_id:
                                        parent_category_id = parent_category_id[0].id
                                    else:
                                        parent_category_id = False
                                else:
                                    parent_category_id = False
                                if row['type']=='normal':
                                    account_asset_id = account_obj.search([('code','=',row['account_asset_id']),('company_id','=',wiz.company_id.id)])
                                    account_depreciation_id = account_obj.search([('code','=',row['account_depreciation_id']),('company_id','=',wiz.company_id.id)])
                                    account_expense_id = account_obj.search([('code','=',row['account_expense_id']),('company_id','=',wiz.company_id.id)])
                                    account_income_id = account_obj.search([('code','=',row['account_income_id']),('company_id','=',wiz.company_id.id)])
                                    categ = categ_obj.create({
                                            'parent_id': parent_category_id,
                                            'code': row['code'],
                                            'name': row['name'],
                                            'type': row['type'],
                                            'asset_type': row['asset_type'],
                                            'method_number_min': row['method_number_min'],
                                            'method_number': row['method_number'],
                                            'sequence_id': row['asset_type']=='fixed' and inv_sequence_id or False,
                                            'account_asset_id': account_asset_id and account_asset_id[0].id or False,
                                            'account_depreciation_id': account_depreciation_id and account_depreciation_id[0].id or False,
                                            'account_expense_depreciation_id': account_expense_id and account_expense_id[0].id or False,
                                            'account_income_id': account_income_id and account_income_id[0].id or False,
                                            'method': row['method'],
                                            'method_time': row['method_time'],
                                            'method_period': row['method_period']
                                    })
                                else:
                                    categ = categ_obj.create({
                                        'parent_id': parent_category_id,
                                        'code': row['code'],
                                        'name': row['name'],
                                        'type': row['type'],
                                        'asset_type': row['asset_type'],
                                    })
                    finally:
                        f.close()
        # Load Bank Statement Operation Templates if not installed previously
        statement_obj = self.env['account.statement.operation.template']
        installed = self.env['ir.module.module'].search([('name','=','l10n_ro_account_bank_statement'),('state','=','installed')])
        if installed:
            wiz = self[0]
            if wiz.bank_statement_template_installed:
                statements = statement_obj.search([('company_id','=',wiz.company_id.id)])
                if not statements:
                    script_dir = os.path.dirname(os.getcwd())
                    rel_path = str(script_dir) + "/l10n-romania/l10n_ro_config/data/account_statement_operation_template.csv"
                    f = open(rel_path, 'rb')
                    try:                     
                        operations = csv.DictReader(f)
                        for row in operations:
                            account_id = account_obj.search([('code','=',row['account_id']),('company_id','=',wiz.company_id.id)])
                            if account_id:
                                statement_obj.create({
                                    'label': row['label'],
                                    'name': row['name'],
                                    'account_id': account_id[0].id,
                                    'amount_type': row['amount_type'],
                                    'amount': row['amount'],
                                    'company_id': wiz.company_id.id,
                                })
                    finally:
                        f.close()
        return res
                        
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
