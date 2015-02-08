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
    @api.model
    def get_worked_day_lines(self, contract_ids, date_from, date_to):
        res = super(hr_payslip, self).get_worked_day_lines(
            contract_ids, date_from, date_to)
        hs_obj = self.pool.get('hr.holidays.status')
        ret = []
        for key, val in enumerate(res):
            hs_ids = hs_obj.search(self.env.cr, self.env.user.id, [('name', '=', val['code'])])
            if hs_ids:
                hs = hs_obj.browse(self.env.cr, self.env.user.id, hs_ids)
                val['code'] = hs.leave_code
            ret += [val]
        return ret

    # overriden to get all inputs
    @api.model
    def get_inputs(self, contract_ids, date_from, date_to):
        res = super(hr_payslip, self).get_inputs(
            contract_ids, date_from, date_to)
        contract_obj = self.pool.get('hr.contract')
        for contract in contract_obj.browse(
                self.env.cr, self.env.user.id, contract_ids):
            for advantage in contract.advantage_ids:
                res += [{
                    'name': advantage.name,
                    'code': advantage.code,
                    'amount': advantage.amount,
                    'contract_id': contract.id,
                }]
        return res

