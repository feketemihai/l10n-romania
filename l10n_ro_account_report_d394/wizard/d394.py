# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Fekete Mihai <mihai.fekete@forbiom.eu>
#    Copyright (C) 2014 FOREST AND BIOMASS SERVICES ROMANIA SA
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

import base64

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class d394_new_report(models.TransientModel):

    """
    D394 Declaration
    """
    _name = "l10n_ro_account_report.d394_new.report"
    _description = 'D394 New Declaration'

    def _get_xml_data(self):
        if self._context.get('file_save', False):
            return base64.encodestring(context['file_save'].encode('utf8'))
        return ''

    @api.multi
    @api.depends('company_id', 'period_id')
    def _get_name(self):
        self.ensure_one()
        name = 'd394'
        if self.company_id and self.company_id.vat:
            name += '_%s' % self.company_id.vat
        if self.period_id:
            name += '_%s' % self.period_id.name
        self.name = name

    file_save = fields.Binary('Save File', default='_get_xml_data')
    name = fields.Char('File Name', compute='_get_name')
    msg = fields.Text('File created', readonly=True,
                      default='Save the File with '".xml"' extension.')
    company_id = fields.Many2one('res.company', 'Company', required=True)
    period_id = fields.Many2one('account.period', 'Period', required=True)
    anaf_cross_opt = fields.Boolean('ANAF Crosschecking',
                                    related='company_id.anaf_cross_opt')
    anaf_cross_new_opt = fields.Boolean('Allow ANAF Crosschecking')

    @api.multi
    def _get_datas(self):
        """"""
        self.ensure_one()
        ctx = dict(self._context)
        obj_invoice = self.env['account.invoice']
        obj_inv_line = self.env['account.invoice.line']
        obj_period = self.env['account.period']
        obj_sequence = self.env['ir.sequence']
        obj_company = self.env['res.company']
        obj_currency = self.env['res.currency']
        obj_partner = self.env['res.partner']
        obj_tax_obj = self.env['account.tax']

        xmldict = {}

        user = self.env.user
        function = email = ''
        if user.partner_id.function:
            function = user.partner_id.function
        else:
            raise UserError(_('You need to define your Job Position.'))
        uid_name = user.partner_id.name.split()
        uid_fname = ' '.join(uid_name[:-1])
        uid_name = uid_name[-1]

        company = self.company_id

        comm_partner = self.company_id.partner_id.commercial_partner_id
        decl_partner = self.company_id.partner_id
        int_partner = user.partner_id.commercial_partner_id

        comp_currency = company.currency_id.id
        period = self.period_id
        # Add period date in context for chacking VAT on Payment option
        ctx1 = ctx.copy()
        ctx1.update({'check_date': self.period_id.date_stop})

        xmldict.update({
            'luna': int(period.code[:2]),
            'an': int(period.code[3:]),
            'tip_D394': "L",
            'sistemTVA': comm_partner.with_context(
                ctx1)._check_vat_on_payment(),
            'op_efectuate': 0,
            'nume_declar': uid_name,
            'prenume_declar': uid_fname,
            'functie_declar': function,
            'caen': company.codcaen.code,
            'cui': comm_partner.vat[2:],
            'den': comm_partner.name,
            'adresa': ', '.join([
                comm_partner.state_id and comm_partner.state_id.name,
                comm_partner.city,
                comm_partner.street,
                comm_partner.zip]),
            'telefon': comm_partner.phone,
            'fax': comm_partner.fax,
            'mail': comm_partner.email,
            'totalPlata_A': 0,
            'cifR': '',
            'denR': '',
            'functie_reprez': '',
            'adresaR': '',
            'telefonR': '',
            'faxR': '',
            'mailR': '',
            'tip_intocmit': bool(int_partner.is_company),
            'den_intocmit': int_partner.name,
            'cif_intocmit': int_partner.vat and int_partner.vat[2:],
            'calitate_intocmit': bool(int_partner.is_company) and \
                int_partner.function or '',
            'functie_intocmit': not bool(int_partner.is_company) and \
                int_partner.function or '',
            'optiune': self.anaf_cross_opt,
            'schimb_optiune': self.anaf_cross_new_opt,
            'nrCui': 0,
            'nrFactL': 0,
            'bazaL': 0,
            'tvaL': 0,
            'nrFactA': 0,
            'bazaA': 0,
            'tvaA': 0,
            'nrFactV': 0,
            'bazaV': 0,
            'tvaV': 0,
            'bazaVc': 0,
            'tvaVc': 0,
            'nrFactC': 0,
            'bazaC': 0,
            'tvaC': 0,
            'bazaCc': 0,
            'tvaCc': 0,
            'informatii': [],
            'rezumat1': [],
            'rezumat2': [],
            'serieFacturi': [],
            'lista': [],
            'facturi': [],
            'op1': [],
            'op2': [],
        })
        if company.email:
            xmldict.update({
                'mailFisc': company.email,
            })
        else:
            xmldict.update({
                'mailFisc': user.partner_id.email or '-',
            })

        if comm_partner.id != decl_partner.id:
            xmldict.update({
                'cifR': decl_partner.vat[2:],
                'denR': decl_partner.name,
                'functie_reprez': decl_partner.function,
                'adresaR': ', '.join([
                    decl_partner.state_id and decl_partner.state_id.name,
                    decl_partner.city,
                    decl_partner.street,
                    decl_partner.zip]),
                'telefonR': decl_partner.phone,
                'faxR': decl_partner.fax,
                'mailR': decl_partner.email,
            })
        from_xml = []
        cui = {}
        totalPlata_A = 0
        nrCui = 0
        nrfactL = bazaL = tvaL = 0
        nrfactA = bazaA = tvaA = 0
        nrfactV = bazaV = tvaV = bazaVc = tvaVc = 0
        nrfactC = bazaC = tvaC = bazaCc = tvaCc = 0
        informatii = []
        rezumat1 = []
        rezumat2 = []
        serieFacturi = []
        lista = []
        facturi = []
        op1 = []
        op2 = []
        oper_types = partner_types = cotas = {}
        invoices = obj_invoice.search([
                    ('state', 'in', ['open', 'paid']),
                    ('period_id', '=', period.id),
                    ('company_id', '=', company.id)
                ])
        oper_types = [invoice.operation_type for invoice in invoices]
        for oper_type in oper_types:
            oper_type_inv = invoices.filtered(
                lambda r: r.operation_type == oper_type)
            partner_types = [
                invoice.partner_type for invoice in oper_type_inv]
            for partner_type in partner_types:
                part_type_inv = oper_type_inv.filtered(
                    lambda r: r.partner_type == partner_type)
                for invoice in part_type_inv:
                    cotas = [tax for tax in invoice.tax_ids]
                for cota in cotas:
                    print cota.name + ' ' + str(cota.amount)
                for cota in cotas:
                    cota_inv = part_type_inv.filtered(
                        lambda r: cota.id in r.tax_ids.ids)
                    partners = [invoice.partner_id for invoice in cota_inv]
                    for partner in partners:
                        part_invoices = cota_inv.filtered(
                            lambda r: r.partner_id.id == partner.id)
                        cota_amount = 0
                        if cota.type == 'percent':
                            cota_amount = int(cota.amount * 100)
                        elif cota.type == 'amount':
                            cota_amount = int(cota.amount)
                        if partner_type == 2:
                            doc_types = [
                                inv.origin_type for inv in part_invoices]
                            for doc_type in doc_types:
                                domain = [('invoice_id',
                                           'in',
                                           part_invoices.ids)]
                                inv_lines = obj_inv_line.search(domain)
                                filtered_inv_lines = []
                                for inv_line in inv_lines:
                                    fp = inv_line.invoice_id.fiscal_position
                                    tax = inv_line.product_id.supplier_taxes_id
                                    if not fp or ('National' in fp.name):
                                        tax = inv_line.invoice_line_tax_id.ids
                                        if tax in [cota.id]:
                                            filtered_inv_lines.append(
                                                inv_line.id)
                                    else:
                                        inv_type = inv_line.invoice_id.type
                                        if inv_type in ('out_invoice',
                                                        'out_refund'):
                                            tax = inv_line.product_id.taxes_id
                                        if tax.ids in [cota.id]:
                                            filtered_inv_lines.append(
                                                inv_line.id)
                                print inv_lines
                                inv_lines = obj_inv_line.browse(
                                    filtered_inv_lines)
                                baza = sum(
                                    line.price_subtotal for line in inv_lines)
                                taxes = 0
                                new_dict = {
                                    'tip': oper_type,
                                    'tip_partener': partner_type,
                                    'cota': cota_amount,
                                    'cuiP': partner._split_vat(partner.vat)[1],
                                    'denP': partner.name,
                                    'nrFact': len(
                                        line.invoice_id for line in inv_lines),
                                    'baza': baza,
                                    'taraP': partner.country_id.code.upper(),
                                    'locP': partner.city_id.name,
                                    'judP': partner.state_id.order_code,
                                    'strP': partner.add_street,
                                    'nrP': partner.add_number,
                                    'blP': partner.add_block,
                                    'apP': partner.add_flat,
                                    'detP': partner.street2,
                                    'tip_document': doc_type,
                                }
                        else:
                            domain = [('invoice_id', 'in', part_invoices.ids)]
                            inv_lines = obj_inv_line.search(domain)
                            filtered_inv_lines = []
                            for inv_line in inv_lines:
                                fp = inv_line.invoice_id.fiscal_position
                                tax = inv_line.product_id.supplier_taxes_id
                                if not fp or ('National' in fp.name):
                                    tax = inv_line.invoice_line_tax_id
                                    if cota.id in tax.ids:
                                        filtered_inv_lines.append(
                                            inv_line.id)
                                else:
                                    inv_type = inv_line.invoice_id.type
                                    if inv_type in ('out_invoice',
                                                    'out_refund'):
                                        tax = inv_line.product_id.taxes_id
                                    if cota.id in tax.ids:
                                        filtered_inv_lines.append(
                                            inv_line.id)
                            inv_lines = obj_inv_line.browse(filtered_inv_lines)
                            print inv_lines
                            baza = sum(
                                line.price_subtotal for line in inv_lines)
                            taxes = 0
                            new_dict = {
                                'tip': oper_type,
                                'tip_partener': partner_type,
                                'cota': cota_amount,
                                'cuiP': partner._split_vat(partner.vat)[1],
                                'denP': partner.name,
                                'nrFact': len(part_invoices),
                                'baza': baza,
                            }
                            if oper_type in ('L', 'V', 'C', 'A', 'AI'):
                                taxes = sum(
                                    line.price_taxes + \
                                    line.price_normal_taxes for line in inv_lines)
                                new_dict['tva'] = taxes
                                products = [line.product_id for line in inv_lines]
                                codes = [product.d394_id for product in products]
                                op11 = []
                                for code in codes:
                                    cod_lines = [
                                        line for line in inv_lines.filtered(
                                            lambda r:
                                            r.product_id.d394_id.id == code.id)
                                    ]
                                    baza1 = sum(
                                        line.price_subtotal for line in cod_lines)
                                    taxes1 = sum(
                                        line.price_taxes + \
                                        line.price_normal_taxes for line in cod_lines)
                                    op11.append({
                                        'codPR': code.name,
                                        'bazaPR': baza1,
                                        'tvaPR': taxes1
                                    })
                                new_dict['op11'] = op11
                        op1.append(new_dict)
        xmldict.update({
            'totalPlata_A': int(len(cui)) + int(bazaL) + int(tvaL) +
            int(bazaA) + int(tvaA) + int(bazaV) + int(tvaV) + int(bazaVc) +
            int(tvaVc) + int(bazaC) + int(tvaC) + int(bazaCc) + int(tvaCc),
            'nrCui': int(len(cui)),
            'nrFactL': nrfactL,
            'bazaL': bazaL,
            'tvaL': tvaL,
            'nrFactA': nrfactA,
            'bazaA': bazaA,
            'tvaA': tvaA,
            'nrFactV': nrfactV,
            'bazaV': bazaV,
            'tvaV': tvaV,
            'bazaVc': bazaVc,
            'tvaVc': tvaVc,
            'nrFactC': nrfactC,
            'bazaC': bazaC,
            'tvaC': tvaC,
            'bazaCc': bazaCc,
            'tvaCc': tvaCc,
            'op1': op1,
        })
        # Change company option regarding ANAF crosschecking
        if self.anaf_cross_new_opt != self.anaf_cross_opt:
            company.anaf_cross_opt = True
        return xmldict

    @api.multi
    def create_xml(self):
        self.ensure_one()
        xml_data = self._get_datas()
        print xml_data
        return xml_data
