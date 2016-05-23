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
from openerp.exceptions import ValidationError

class hr_payslip_worked_days(models.Model):
    _inherit = 'hr.payslip.worked_days'

    daily_base = fields.Float(_('Daily Base'))
    employer_days = fields.Integer(_('# Days by Employer'))
    budget_days = fields.Integer(_('# Days by Social Security'))
    employer_amount = fields.Float(_('Amount by Employer'))
    budget_amount = fields.Float(_('Amount by Social Sevcurity'))
    total_amount = fields.Float(_('Total Amount'))


class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    @api.one
    def get_wage_history(self):
        wg_hist = self.env['hr.wage.history']
        start_date = self.date_from[:8] + '01'
        rs = wg_hist.search([('date', '=', start_date)])
        rs.ensure_one()
        return rs

    @api.model
    def get_worked_day_lines(self, contract_ids, date_from, date_to):
        """
        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be
                 applied for the given contract between date_from and date_to
        """
        def was_on_leave(employee_id, datetime_day):
            res = False
            day = datetime_day.strftime("%Y-%m-%d")
            res = self.env['hr.holidays'].search([
                ('state', '=', 'validate'),
                ('employee_id', '=', employee_id),
                ('type', '=', 'remove'),
                ('date_from', '<=', day),
                ('date_to', '>=', day)])
            return res

        res = []
        for contract in self.env['hr.contract'].browse(contract_ids):
            if not contract.working_hours:
                # fill only if the contract as a working schedule linked
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
            day_from = datetime.strptime(date_from, "%Y-%m-%d")
            day_to = datetime.strptime(date_to, "%Y-%m-%d")
            nb_of_days = (day_to - day_from).days + 1
            for day in range(0, nb_of_days):
                working_hours_on_day =\
                    self.env['resource.calendar'].working_hours_on_day(
                        contract.working_hours,
                        day_from + timedelta(days=day))
                if working_hours_on_day:
                    # the employee had to work
                    emp_leaves = was_on_leave(contract.employee_id.id,
                                              day_from + timedelta(days=day))
                    if emp_leaves:
                        # if he was on leave, fill the leaves dict
                        for leave in emp_leaves:
                            if leave.holiday_status_id.leave_code:
                                leave_code = leave.holiday_status_id.leave_code
                            else:
                                leave_code = leave.holiday_status_id.name
                            if leave_code in leaves:
                                leaves[leave_code]['number_of_days'] += 1.0
                                leaves[leave_code]['number_of_hours'] +=\
                                    working_hours_on_day
                                if day_from + timedelta(days=day) == fields.Date.from_string(leave.date_from):
                                    leaves[leave_code]['employer_days'] +=\
                                        leave.employer_days
                                    leaves[leave_code]['budget_days'] +=\
                                        leave.budget_days
                                    leaves[leave_code]['employer_amount'] +=\
                                        leave.employer_amount
                                    leaves[leave_code]['budget_amount'] +=\
                                        leave.budget_amount
                                    leaves[leave_code]['total_amount'] +=\
                                        leave.total_amount
                            else:
                                leaves[leave_code] = {
                                    'name': leave.holiday_status_id.name,
                                    'sequence': 5,
                                    'code': leave_code,
                                    'number_of_days': 1.0,
                                    'number_of_hours': leave.number_of_days_temp * 8,
                                    'contract_id': contract.id,
                                    'daily_base': leave.daily_base,
                                    'employer_days': leave.employer_days,
                                    'budget_days': leave.budget_days,
                                    'employer_amount': leave.employer_amount,
                                    'budget_amount': leave.budget_amount,
                                    'total_amount': leave.total_amount,
                                }
                    else:
                        # add the input vals to tmp (increment if existing)
                        attendances['number_of_days'] += 1.0
                        attendances['number_of_hours'] += working_hours_on_day
            leaves = [value for key, value in leaves.items()]
            res += [attendances] + leaves
        return res

    @api.multi
    def process_sheet(self):
        for slip in self:
            slip.line_ids.unlink()
            self.get_worked_day_lines(slip.contract_id.id, slip.date_from, slip.date_to)
        res = super(hr_payslip, self).process_sheet()
        for slip in self:
            days = hours = gross = net = 0.00
            date_from = date_to = False
            date_from = slip.date_from
            date_to = slip.date_to
            worked_days = slip.worked_days_line_ids
            if worked_days:
                days = sum(line.number_of_days for line in worked_days)
                hours = sum(line.number_of_hours for line in worked_days)
            try:
                gross_id = self.env.ref('l10n_ro_hr_payroll.venitbrut')
                if gross_id:
                    gross_line_id = self.env['hr.payslip.line'].search(
                        [
                         ('slip_id', '=', slip.id),
                         ('salary_rule_id', '=', gross_id[0].id)
                        ])
                    if gross_line_id:
                        gross = gross_line_id[0].total
                else:
                    ValidationError(_("There were no predefined gross "
                                      "salary rule."))
                net_id = self.env.ref('l10n_ro_hr_payroll.salar_net')
                if net_id:
                    net_line_id = self.env['hr.payslip.line'].search(
                        [
                         ('slip_id', '=', slip.id),
                         ('salary_rule_id', '=', net_id[0].id)
                        ])
                    if net_line_id:
                        net = net_line_id[0].total
                else:
                    ValidationError(_("There were no predefined net "
                                      "salary rule."))
                self.env['hr.employee.income'].create({
                    'employee_id': slip.employee_id.id,
                    'payslip_id': slip.id,
                    'date_from': date_from,
                    'date_to': date_to,
                    'number_of_days': days,
                    'number_of_hours': hours,
                    'gross_amount': gross,
                    'net_amount': net,
                })
            except:
                ValidationError(_("The payslip data was not added to the "
                                  "employee income history."))
        return res

    @api.one
    @api.depends('worked_days_line_ids')
    def _get_working_days(self):
        self.working_days = sum(line.number_of_days for line in self.worked_days_line_ids)

    working_days = fields.Integer(_('# Working Days'), compute='_get_working_days', store=True)


class hr_salary_rule(models.Model):
    _inherit = 'hr.salary.rule'

    def compute_rule(self, cr, uid, rule_id, localdict, context=None):
        working_days = sum(
            [localdict['worked_days'].dict[x].number_of_days
             for x in localdict['worked_days'].dict])
        working_hours = sum(
            [localdict['worked_days'].dict[x].number_of_hours
             for x in localdict['worked_days'].dict])

        localdict.update({
            'working_days_hours': (working_days, working_hours),
        })

        return super(hr_salary_rule, self).compute_rule(
             cr, uid, rule_id, localdict, context
        )
