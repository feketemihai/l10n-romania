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

from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _


class hr_employee_income(models.Model):
    _name = 'hr.employee.income'
    _description = 'Employee income from payslips'

    @api.one
    @api.onchange('payslip_id')
    def _onchange_payslip_id(self):
        days = hours = gross = net = 0.00
        date_from = date_to = False
        if self.payslip_id:
            date_from = self.payslip_id.date_from
            date_to = self.payslip_id.date_to
            worked_days = self.payslip_id.worked_days_line_ids
            if worked_days:
                days = sum(line.number_of_days for line in worked_days)
                hours = sum(line.number_of_hours for line in worked_days)
            gross_id = self.env.ref('l10n_ro_hr_payroll.venit_brut')
            if gross_id:
                gross_line_id = self.env['hr.payslip.line'].search(
                    [
                     ('slip_id', '=', self.payslip_id.id),
                     ('salary_rule_id', '=', gross_id[0].id)
                    ])
                if gross_line_id:
                    gross = gross_line_id[0].total
            net_id = self.env.ref('l10n_ro_hr_payroll.salarnet')
            if net_id:
                net_line_id = self.env['hr.payslip.line'].search(
                    [
                     ('slip_id', '=', self.payslip_id.id),
                     ('salary_rule_id', '=', net_id[0].id)
                    ])
                if net_line_id:
                    net = net_line_id[0].total
        self.write(
            {
             'number_of_days': days,
             'number_of_hours': hours,
             'gross_amount': gross,
             'net_amount': net,
             'date_from': date_from,
             'date_to': date_to
            })

    employee_id = fields.Many2one('hr.employee', 'Employee',
                                  required=True, index=True)
    payslip_id = fields.Many2one('hr.payslip', 'Payslip')
    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date To', required=True)
    number_of_days = fields.Integer('Number of Days', required=True)
    number_of_hours = fields.Integer('Number of Hours', required=True)
    gross_amount = fields.Float('Gross Income', required=True)
    net_amount = fields.Float('Net Salary', required=True)


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    income_ids = fields.One2many('hr.employee.income', 'employee_id',
                                 'Payslip History')

    def _get_holiday_base(self, date=False):
        if not date:
            date = field.Date.today()
        six_month = date + relativedelta(months=-6)
        
        income_ids = self.income_ids.filtered(lambda income: income.date_to <= date and income.date_from >= six_month)
        days = gross = False
        if income_ids:
            gross = sum(income.gros_amount for income in income_ids)
            days = sum(income.number_of_days for income in income_ids)
        if gross and days and days != 0.00:
            return gross / days
        return True

    def _get_payslips(self, limit=None):
        return self.env['hr.payslip'].search(
            [('employee_id', '=', employee_id), ('state', '=', 'done')])
