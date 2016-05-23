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

    meal_voucher_value = fields.Float('Meal Voucher Value')
    
    @api.model
    def get_medium_wage(self, date=False):
        if not date:
            date = field.Date.today()
        res = self.env['hr.wage.history'].search([('date', '<=', date)])
        return res[0].med_wage

    @api.model
    def get_minimum_wage(self, date=False):
        if not date:
            date = field.Date.today()
        res = self.env['hr.wage.history'].search([('date', '<=', date)])
        return res[0].min_wage

    @api.model
    def get_ceiling(self, date=False):
        if not date:
            date = field.Date.today()
        res = self.env['hr.wage.history'].search([('date', '<=', date)])
        return res[0].ceiling_min_wage
        
