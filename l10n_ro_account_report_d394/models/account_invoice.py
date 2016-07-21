# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Fekete Mihai <mihai.fekete@forbiom.eu>
#    Copyright (C) 2016 FOREST AND BIOMASS SERVICES ROMANIA SA
#    (http://www.forbiom.eu).
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

import re
from openerp import models, fields, api

ORIGIN_TYPE = [
    ('1', 'Invoice'),
    ('2', 'Slip'),
    ('3', 'Trading Book'),
    ('4', 'Contract')
]

OPERATION_TYPE = [
    ('L', 'Customer Invoice'),
    ('A', 'Supplier Invoice'),
    ('LS', 'Special Customer Invoice'),
    ('AS', 'Special Supplier Invoice'),
    ('AI', 'VAT on Payment Supplier Invoice'),
    ('V', 'Inverse Taxation Customer Invoice'),
    ('C', 'Inverse Taxation Supplier Invoice'),
    ('N', 'Fizical Persons Supplier Invoice')
]

SEQUENCE_TYPE = [
    ('normal', 'Invoice'),
    ('autoinv1', 'Customer Auto Invoicing'),
    ('autoinv2', 'Supplier  Auto Invoicing')
]


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    fiscal_receipt = fields.Boolean('Fiscal Receipts Journal')


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    @api.depends('state')
    def _get_inv_number(self):
        regex = re.compile('[^a-zA-Z]')
        regex1 = re.compile('[^0-9]')
        for inv in self:
            if inv.internal_number:
                inv_seq = inv.journal_id.sequence_id
                ctx = self._context.copy()
                ctx['fiscalyear_id'] = inv.period_id.fiscalyear_id.id
                inv_serie = inv_seq._interpolate(
                    inv_seq.prefix,
                    inv_seq.with_context(ctx)._interpolation_dict_context())
                inv.inv_serie = regex.sub('', inv_serie)
                inv.inv_number = regex1.sub(
                    '',
                    inv.internal_number.replace(inv_serie, ''))
        return True

    @api.multi
    @api.depends('state')
    def _get_partner_type(self):
        for inv in self:
            partner = inv.partner_id
            eur_countries = []
            eur_grp = self.env.ref('base.europe')
            if eur_grp:
                eur_countries = [country.id for country in eur_grp.country_ids]
            if partner.country_id and \
                    partner.country_id.id == self.env.ref('base.ro').id:
                if partner.vat_subjected:
                    new_type = '1'
                else:
                    new_type = '2'
            elif partner.country_id.id in eur_countries:
                new_type = '3'
            else:
                new_type = '4'
            inv.partner_type = new_type
        return True

    @api.multi
    @api.depends('state')
    def _get_operation_type(self):
        for inv in self:
            if inv.type in ('out_invoice', 'out_refund'):
                if inv.fiscal_position and \
                        ('Taxare Inversa' in inv.fiscal_position.name):
                    oper_type = 'V'
                elif not inv.fiscal_position or \
                        (inv.fiscal_position and \
                         ('National' in inv.fiscal_position.name)):
                    if inv.special_taxes:
                        oper_type = 'LS'
                    else:
                        oper_type = 'L'
                else:
                    oper_type = 'L'
            else:
                if not inv.partner_id.is_company and inv.origin_type:
                    oper_type = 'N'
                elif inv.fiscal_position and \
                        (('Taxare Inversa' in inv.fiscal_position.name) or \
                         ('Comunitar' in inv.fiscal_position.name) or \
                         ('Scutite' in inv.fiscal_position.name)):
                    oper_type = 'C'
                elif not inv.fiscal_position or \
                        (inv.fiscal_position and
                         ('National' in inv.fiscal_position.name)):
                    if inv.special_taxes:
                        oper_type = 'AS'
                    elif inv.vat_on_payment:
                        oper_type = 'AI'
                    else:
                        oper_type = 'A'
                elif inv.vat_on_payment:
                    oper_type = 'AI'
                else:
                    oper_type = 'A'
            inv.operation_type = oper_type
        return True

    @api.multi
    @api.depends('state')
    def _get_tax_ids(self):
        for inv in self:
            check = False
            taxes = []
            if not inv.fiscal_position or ('National' in \
                    inv.fiscal_position.name):
                for line in inv.invoice_line:
                    taxes += [tax.id for tax in line.invoice_line_tax_id]
            else:
                for line in inv.invoice_line:
                    if inv.type in ('out_invoice', 'out_refund'):
                        taxes += [tax.id for tax in line.product_id.taxes_id]
                    else:
                        taxes += [tax.id for tax in \
                            line.product_id.supplier_taxes_id]
            inv.tax_ids = taxes
        return True

    @api.multi
    def _check_special_taxes(self):
        self.ensure_one()
        check = False
        for tax_line in self.tax_line:
            if any(i in tax_line.name for i in (' 9', ' 5')):
                check = True
        return check

    origin_type = fields.Selection(ORIGIN_TYPE, default='1')
    sequence_type = fields.Selection(SEQUENCE_TYPE,
                                     related='journal_id.sequence_type')
    operation_type = fields.Selection(OPERATION_TYPE,
                                      compute='_get_operation_type')
    inv_serie = fields.Char('Invoice Serie',
                            compute="_get_inv_number")
    inv_number = fields.Char('Invoice Number',
                             compute="_get_inv_number")
    partner_type = fields.Char('D394 Partner Type',
                               compute="_get_partner_type")
    special_taxes = fields.Boolean('Special Taxation')
    tax_ids = fields.Many2many('account.tax',
                               compute="_get_tax_ids")

    @api.multi
    def onchange_journal_id(self, journal_id=False):
        res = super(AccountInvoice, self).onchange_journal_id(journal_id)
        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
            res['value']['fiscal_receipt'] = bool(journal.fiscal_receipt)
        return res
