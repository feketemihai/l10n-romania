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

from datetime import datetime, timedelta
from openerp import models, fields, api, _

class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    # overridden to get proper leave codes
    @api.model
    def get_worked_day_lines(self, contract_ids, date_from, date_to):
        # pot sa am 10 contracte dar unul singur de salar
        res = []
        day_from = datetime.strptime(date_from,"%Y-%m-%d")
        day_to = datetime.strptime(date_to,"%Y-%m-%d")
        nb_of_days = (day_to - day_from).days + 1
        # cal_obj = self.env['resource.calendar'] mumu old vs new api
        cal_obj = self.pool.get('resource.calendar')
        hol_obj = self.env['hr.holidays']
        for contract in self.env['hr.contract'].browse(contract_ids):
            if not contract.working_hours:
                #fill only if the contract as a working schedule linked
                continue
            attendances = {
                 'name': _("Normal Working Days paid at 100%"),
                 'sequence': 1,
                 'code': 'WORK100',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            leaves = {}
            for day in range(0, nb_of_days):
                curr_day = day_from + timedelta(days=day)
                curr_day = curr_day.replace(hour=0, minute=0)
                # TODO functia working_hours_on_day e trecuta la depricated
                # dar cum am spus si mai sus, mumu old vs new api
                working_hours_on_day = cal_obj.get_working_hours_of_date(self.env.cr, self.env.uid, contract.working_hours.id, start_dt=curr_day, context=None)
                 # cal_obj.working_hours_on_day(contract.working_hours, curr_day)
                leave = hol_obj.search([
                    ('state', '=', 'validate'),
                    ('employee_id', '=', contract.employee_id.id),
                    ('type', '=', 'remove'),
                    ('date_from', '<=', curr_day.strftime("%Y-%m-%d")),
                    ('date_to', '>=', curr_day.strftime("%Y-%m-%d"))
                ])
                if leave and working_hours_on_day:
                    leave_type = leave.holiday_status_id.leave_code
                    #if he was on leave, fill the leaves dict
                    if leave_type in leaves:
                        leaves[leave_type]['number_of_days'] += 1.0
                        leaves[leave_type]['number_of_hours'] += working_hours_on_day
                    else:
                        leaves[leave_type] = {
                            'name': leave.name,
                            'sequence': 5,
                            'code': leave_type,
                            'number_of_days': 1.0,
                            'number_of_hours': working_hours_on_day,
                            'contract_id': contract.id,
                        }
                elif working_hours_on_day:
                    #add the input vals to tmp (increment if existing)
                    attendances['number_of_days'] += 1.0
                    attendances['number_of_hours'] += working_hours_on_day
            res += [attendances] + leaves.values()
        return res
        
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

