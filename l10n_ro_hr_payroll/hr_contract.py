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

class hr_contract(models.Model):
    _inherit = 'hr.contract'

    meal_voucher = fields.Boolean('Meal Voucher?')
    meal_voucher_value = fields.Float(
        'Meal Voucher Value', decimal=(0,2), default = 9.35)
    programmer_or_handicaped = fields.Boolean(
        'Programmer or Handicaped', default = False)

    def compute_avg_minimum_wage(self, months):
        wg_hist = self.pool.get('hr.wage.history')
        rs = wg_hist.search([
            ('history_type', '=', 0),
        ])
        print rs

    def compute_avg_medimum_wage(self, months):
        wg_hist = self.pool.get('hr.wage.history')
        rs = wg_hist.search([
            ('history_type', '=', 1),
        ])
        print rs

    def compute_avg_wage(self, months):
        wg_hist = self.pool.get('hr.wage.history')
        rs = wg_hist.search([
            ('history_type', '=', 2),
            ('employee_id', '=', self.employee_id.id)
        ])
        print rs

class hr_wage_history_line(models.Model):
    _name = 'hr.wage.history.line'
    _description = ''
    _rec_name = 'month'
    _order = 'month desc'

    month = fields.Selection([
            (1, _('January')), (2, _('February')), (3, _('March')),
            (4, _('April')), (5, _('May')), (6, _('June')), (7, _('July')),
            (8, _('August')), (9, _('September')), (10, _('Octomber')),
            (11, _('November')), (12, _('December')),
        ], required = True, index = True)
    wage = fields.Integer('Wage', required = True)
    working_days = fields.Integer('Number of Working(ed) Days', required = True)
    history_id = fields.Many2one(
        'hr.wage.history', 'Wage History', required = True)

class hr_wage_history(models.Model):
    _name = 'hr.wage.history'
    _description = 'Used to compute taxable base'
    _rec_name = 'year'
    _order = 'year desc'
    _sql_constrains = [(
        'year_type_employee_uniq',
        'unique (year, history_type, employee_id)',
        'Only one type per year and employee'
    )]

    year = fields.Integer('Year', required = True)
    line_ids = fields.One2many(
        'hr.wage.history.line', 'history_id', 'Wage History Lines')
    history_type = fields.Selection([
            (0, 'Minimum Wage'),
            (1, 'Medium Wage'),
            (2, 'Employee Wage'),
        ], index = True)
    employee_id = fields.Many2one('hr.employee', 'Employee')

    @api.one
    def _compute_avg(self, start_month = 1):
        wage = working_days = 0
        for line in self.line_ids.search([['month', '>=', start_month]]):
            wage += line.wage
            working_days += line.working_days
        return float(wage / working_days)
