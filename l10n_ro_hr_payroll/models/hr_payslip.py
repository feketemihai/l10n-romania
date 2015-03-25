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
import pytz

from openerp import models, fields, api, tools, _

class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    @api.one
    def get_wage_history(self):
        wg_hist = self.env['hr.wage.history']
        start_date = self.date_from[:8] + '01'
        rs = wg_hist.search([('date', '=', start_date)])
        rs.ensure_one()
        print rs
        return rs

    def _get_calendar_leaves(self, resource_id, day_from, day_to):
        cal_leaves = {}
        DFMT = tools.DEFAULT_SERVER_DATETIME_FORMAT
        self.env.cr.execute("""
        SELECT
            id, holiday_id, date_from, date_to
        FROM
            resource_calendar_leaves
        WHERE
            resource_id = %d
        AND (date_from, date_to) OVERLAPS ('%s'::TIMESTAMP, '%s'::TIMESTAMP)
        """ % (resource_id, str(day_from), str(day_to)))
        cal_leaves = {}
        for x in self.env.cr.fetchall():
            leave = {
                'leave': self.env['hr.holidays'].browse(x[1]),
                'period': (
                    datetime.strptime(x[2], DFMT),
                    datetime.strptime(x[3], DFMT)
                ),
                'date_period': (
                    datetime.strptime(x[2], DFMT).date(),
                    datetime.strptime(x[3], DFMT).date()
                ),
            }
            cal_leaves.update({x[0]: leave})
        return cal_leaves

    def _was_on_leave(self, day, calendar_leaves):
        res = []
        for x in calendar_leaves:
            if day >= calendar_leaves[x]['date_period'][0] and \
                    day <= calendar_leaves[x]['date_period'][1]:
                res += [(
                    calendar_leaves[x]['leave'],
                    calendar_leaves[x]['period']
                )]
        return res

    # overridden to get proper leave codes
    @api.model
    def get_worked_day_lines(self, contract_ids, date_from, date_to):
        # pot sa am 10 contracte dar unul singur de salar
        res = []
        day_from = datetime.strptime(date_from,"%Y-%m-%d").replace(
            hour = 0, minute = 0, second = 0)
        day_to = datetime.strptime(date_to,"%Y-%m-%d").replace(
            hour = 23, minute = 59, second = 59)
        nb_of_days = (day_to - day_from).days + 1
    
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

            calendar_leaves = self._get_calendar_leaves(
                contract.employee_id.id, day_from, day_to)
            leaves = {}
            for day in range(0, nb_of_days):
                curr_day = (day_from + timedelta(days = day)).\
                    replace(hour=0,minute=0)
                _leave = self._was_on_leave(curr_day.date(), calendar_leaves)
                if _leave == []:
                    leave_int = []
                else:
                    leave_int = [x[1] for x in _leave]
                working_hours = contract.working_hours.\
                    get_working_hours_of_date(
                        start_dt = curr_day,
                        compute_leaves = True,
                        leaves = leave_int).pop()
                if working_hours < 1.0:
                    working_hours = 0.0

                if _leave != []:
                    leave_hours = contract.working_hours.\
                        get_working_hours_of_date(
                            start_dt = curr_day, compute_leaves = False).pop()
                    leave_hours_left = 0.0   
                    for leave, leave_int in _leave:
                        leave_type = leave.holiday_status_id.leave_code
                        _hours = contract.working_hours.\
                            get_working_hours_of_date(
                                start_dt = curr_day,
                                compute_leaves = True,
                                leaves = [leave_int]).pop()

                        leave_hours_left += round(leave_hours - _hours)
                        if leave_type in leaves.keys():
                            leaves[leave_type].update({
                                'number_of_days': leaves[leave_type]['number_of_days'] + leave.number_of_days_temp,
                                'number_of_hours':  leaves[leave_type]['number_of_hours'] + round(leave_hours - _hours)
                            })
                        else:
                            leaves[leave_type] = {
                                'name': leave.name or 'Legal Leaves',
                                'sequence': 5,
                                'code': leave_type,
                                'number_of_days': leave.number_of_days_temp,
                                'number_of_hours': round(leave_hours - _hours),
                                'contract_id': contract.id,
                            }
                    working_hours = leave_hours - leave_hours_left
                    attendances['number_of_hours'] += working_hours
                elif working_hours > 0.0:
                    attendances['number_of_days'] += 1.0
                    attendances['number_of_hours'] += working_hours
            res += [attendances] + leaves.values()
        return res

    # overriden to get all inputs
    @api.model
    def get_inputs(self, contract_ids, date_from, date_to):
        res = super(hr_payslip, self).get_inputs(
            contract_ids, date_from, date_to)
        contract_obj = self.pool.get('hr.contract')
        for contract in contract_obj.browse(
                self.env.cr, self.env.user.id, contract_ids):
            for advantage in contract.advantage_ids:
                amount = advantage.amount
                if advantage.code == 'TICHM':
                    meals = self.env['hr.meal.vouchers'].search([('company_id','=', contract.employee_id.company_id.id),('date_from','>=', date_from),('date_to','<=', date_to)])
                    if meals:
                        meal_vouchers = self.env['hr.meal.vouchers.line'].search([('employee_id','=', contract.employee_id.id),('meal_voucher_id','=', meals[0].id)])
                        if meal_vouchers:
                            amount = sum(voucher.num_vouchers for voucher in meal_vouchers) * contract.employee_id.company_id.meal_voucher_value
                res += [{
                    'name': advantage.name,
                    'code': advantage.code,
                    'amount': amount,
                    'contract_id': contract.id,
                }]
        return res

