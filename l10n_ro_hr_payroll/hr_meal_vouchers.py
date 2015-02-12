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

import time
from datetime import datetime, timedelta
from dateutil import relativedelta
from openerp import netsvc, models, fields, api, _
from openerp.exceptions import ValidationError, Warning

class hr_meal_vouchers_line(models.Model):
    _name = 'hr.meal.vouchers.line'
    _description = 'hr_meal_vouchers'

    meal_voucher_id = fields.Many2one('hr.meal.vouchers', 'Meal Voucher Run')
    contract_id = fields.Many2one('hr.contract', 'Contract')
    worked_days = fields.Integer('# of Worked Days')
    serial_from = fields.Char('Serial # from')
    serial_to = fields.Char('Serial # to')
    
class hr_meal_vouchers(models.Model):
    _name = 'hr.meal.vouchers'
    _description = 'hr_meal_vouchers'
    
    name = fields.Char()
    company_id = fields.Many2one(
        'res.company', 'Company',
        default = lambda self: self.env.user.company_id)
    date_from = fields.Date(
        'Date From', required = True,
        default = lambda *a: time.strftime('%Y-%m-01'))
    date_to = fields.Date(
        'Date To', required = True,
        default = lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
    line_ids = fields.One2many('hr.meal.vouchers.line', 'meal_voucher_id')

    def get_contracts(self):
        angajati = self.env['hr.employee'].search([
            ('company_id', '=', self.company_id.id),
            ('active', '=', True),
        ])
        # TODO: contracte susp
        # [('employee_id', '=', [1,4]), '|', '|', '&', ('date_end', '<=', '2015-02-28'), ('date_end', '>=', '2015-02-01'), '&', ('date_start', '<=', '2015-02-28'), ('date_start', '>=', '2015-02-01'), '&', ('date_start', '<=', '2015-02-01'), '|', ('date_end', '=', False), ('date_end', '>=', '2015-02-28')]
        clause = [('employee_id', 'in', angajati.ids), '|', '|']
        clause += ['&',('date_end', '<=', self.date_to),('date_end','>=', self.date_from)]
        #OR if it starts between the given dates
        clause += ['&',('date_start', '<=', self.date_to),('date_start','>=', self.date_from)]
        #OR if it starts before the date_from and finish after the date_end (or never finish)
        clause += ['&',('date_start','<=', self.date_from),'|',('date_end', '=', False),('date_end','>=', self.date_to)]
        return self.env['hr.contract'].search(clause)

    def get_worked_days_num(self, contract):
        res = 0.0
        day_from = datetime.strptime(self.date_from,"%Y-%m-%d")
        day_to = datetime.strptime(self.date_to,"%Y-%m-%d")
        nb_of_days = (day_to - day_from).days + 1
        # cal_obj = self.env['resource.calendar'] mumu old vs new api
        cal_obj = self.pool.get('resource.calendar')
        hol_obj = self.env['hr.holidays']
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
            if not leave and working_hours_on_day:
                #add the input vals to tmp (increment if existing)
                res += 1.0
        return (contract, res)

    def build_lines(self):
        contracts = self.get_contracts()
        if contracts is False:
            return False
        build = []
        for contract in contracts:
            for advantage in contract.advantage_ids:
                if advantage.code in 'TICHM':
                    line = self.get_worked_days_num(contract)
                    if line[1] > 0:
                        build += [line]
        return build
