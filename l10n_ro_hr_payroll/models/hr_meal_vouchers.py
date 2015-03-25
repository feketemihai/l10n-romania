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
from dateutil.relativedelta import relativedelta
from openerp import netsvc, models, fields, api, _
from openerp.exceptions import ValidationError, Warning

class hr_meal_vouchers_line(models.Model):
    _name = 'hr.meal.vouchers.line'
    _description = 'hr_meal_vouchers'

    meal_voucher_id = fields.Many2one(
        'hr.meal.vouchers', _('Meal Voucher Run'))
    employee_id = fields.Many2one('hr.employee', _('Employee'))
    contract_id = fields.Many2one('hr.contract', _('Contract'), select = True)
    num_vouchers = fields.Integer(_('# of Vouchers'))
    serial_from = fields.Char(_('Serial # from'))
    serial_to = fields.Char(_('Serial # to'))
    
class hr_meal_vouchers(models.Model):
    _name = 'hr.meal.vouchers'
    _description = 'hr_meal_vouchers'

    @api.one
    @api.depends('date_from', 'date_to')
    def _compute_name(self):
        self.name = _("Period %s - %s") % (self.date_from, self.date_to)

    name = fields.Char(compute = "_compute_name", readonly = True)
    company_id = fields.Many2one(
        'res.company', _('Company'),
        default = lambda self: self.env.user.company_id)
    date_from = fields.Date(
        'Date From', required = True,
        default = lambda *a: time.strftime('%Y-%m-01'))
    date_to = fields.Date(
        'Date To', required = True,
        default = lambda *a: str((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))
    line_ids = fields.One2many('hr.meal.vouchers.line', 'meal_voucher_id')

    def get_contracts(self):
        angajati = self.env['hr.employee'].search([
            ('company_id', '=', self.company_id.id),
            ('active', '=', True),
            ('company_id.meal_voucher_value', '!=', 0.0)
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
        return self.env['hr.payslip'].get_worked_day_lines(contract, self.date_from, self.date_to)[0]['number_of_days']

    @api.one
    def build_lines(self):
        lines_obj = self.env['hr.meal.vouchers.line']
        contracts = self.get_contracts()
        for line in lines_obj.search([('contract_id', 'in', contracts.ids)]):
            line.unlink()

        for contract in contracts:
            for advantage in contract.advantage_ids:
                if advantage.code in 'TICHM':
                    no = self.get_worked_days_num(contract.id)
                    if no > 0.0:
                        line = lines_obj.create({
                            'meal_voucher_id': self.id,
                            'employee_id': contract.employee_id.id,
                            'contract_id': contract.id,
                            'num_vouchers': no,
                        })
        return True
