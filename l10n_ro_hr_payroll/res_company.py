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

class res_company_payroll_taxes(models.Model):
    _name = "res.company.payroll.taxes"
    _description = "Payroll Taxes Generic Model"

    code = fields.Char('Tax Code', required = True)
    name = fields.Char('Tax Name', required = True)
    value = fields.Float('Tax Value', required = True)

class res_company_payroll(models.Model):
    _name = "res.company.payroll"
    _description = "Payroll Taxes and Misc"

    name = fields.Char('Paroll Name', required = True)
    minimum_wage = fields.Integer('Minimum Wage', required = True)
    medimum_wage = fields.Integer('Medimum Wage', required = True)
    
    payroll_taxes = fileds.One2many('res.company.payroll.taxes')

class res_company(models.Model):
    _inherit = 'res.company'

    payroll = fields.Many2one('res.company.payroll')

    @api.one
    def get_minimum_wage(self):
        pass

    @api.one
    def get_medimum_wage(self):
        pass

    @api.one
    def get_tax_by_code(self):
        pass

