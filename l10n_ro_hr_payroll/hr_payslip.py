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

class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    # overridden to get proper leave codes
    def get_worked_day_lines(
            self, cr, uid, contract_ids, date_from, date_to, context=None):
        res = super(hr_payslip, self).get_worked_day_lines(
            cr, uid, contract_ids, date_from, date_to, context)
        hs_obj = self.pool.get('hr.holidays.status')
        ret = []
        for key, val in enumerate(res):
            hs_ids = hs_obj.search(cr, uid, [('name', '=', val['code'])])
            if hs_ids:
                hs = hs_obj.browse(cr, uid, hs_ids)
                val['code'] = hs.leave_code
            ret += [val]
        return ret

    # overriden to get all inputs
    def get_inputs(
            self, cr, uid, contract_ids, date_from, date_to, context=None):
        res = super(hr_payslip, self).get_inputs(
            cr, uid, contract_ids, date_from, date_to, context)
        contract_obj = self.pool.get('hr.contract')
        for contract in contract_obj.browse(
                cr, uid, contract_ids, context=context):
            if contract.meal_voucher:
                res += [{
                    'name': u'Tichete de Masă',
                    'code': 'TCHM',
                    'amount': contract.meal_voucher_value,
                    'contract_id': contract.id,
                }]
        return res

