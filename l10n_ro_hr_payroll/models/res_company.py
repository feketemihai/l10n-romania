# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Adrian Vasile <adrian.vasile@gmail.com>
#    Copyright (C) 2014 Adrian Vasile
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

class res_company(models.Model):
    _inherit = 'res.company'

    payroll_taxes = fields.One2many('res.company.payrolltaxes', 'company_id', 'Company Payroll Taxes')
    meal_voucher_value = fields.Float('Meal Voucher Value')

    def get_tax(self, code): 
        if self.payroll_taxes:
            ret = self.payroll_taxes.search([('code', '=', code)])
            if ret and ret.value:
                return ret.value
        return False

class res_company_payroll_taxes(models.Model):
    _name = "res.company.payrolltaxes"
    _description = "res_company_payrolltaxes"
    _sql_constrains = [(
        'company_id_code_uniq',
        'unique (company_id, code)',
        'Unique codes per company'
    )]
    company_id = fields.Many2one('res.company', 'Company', required = True)
    code = fields.Char('Tax Code', required = True)
    name = fields.Char('Tax Name', required = True)
    value = fields.Float('Tax Value', required = True)

