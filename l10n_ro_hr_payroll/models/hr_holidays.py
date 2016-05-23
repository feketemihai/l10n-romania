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
from openerp import tools, models, fields, api, _
from openerp.exceptions import ValidationError, Warning
from openerp.osv import osv


class hr_holidays_status(models.Model):
    _inherit = 'hr.holidays.status'

    _sql_constrains = [(
        'sick_leave_uniq',
        'unique (is_sick_leave, emergency, indemn_code)',
        'Only one Indemnization Code/Emergency pair',
    )]

    @api.one
    @api.depends('name')
    def _compute_leave_code(self):
        if self.is_sick_leave is True:
            self.leave_code = 'SL' + self.indemn_code
        else:
            self.leave_code = ''.join(x[0] for x in self.name.split()).upper()

    @api.one
    @api.onchange('is_sick_leave')
    @api.constrains('indemn_code', 'percentage', 'employer_days', 'max_days')
    def _require_values(self):
        if self.is_sick_leave is True:
            if not self.indemn_code:
                raise ValidationError(_('Set Indemnization Code'))
            if not self.percentage:
                raise ValidationError(_('Set Percentage'))
            if self.employer_days is False:
                raise ValidationError(_('Set # of Days by Employer'))
            if not self.max_days:
                raise ValidationError(_('Set Maximum # of Days'))

    leave_code = fields.Char(
        'Leave Code', compute = '_compute_leave_code', store = True)

    is_sick_leave = fields.Boolean(_('Is Sick Leave'), default = False)
    is_unpaid = fields.Boolean(_('Is Unpaid'), default = False)
    emergency = fields.Boolean(_('Medical Emergency'), default = False)
    indemn_code = fields.Char(_('Indemnization Code'))
    percentage = fields.Integer(_('Percentage'))
    employer_days = fields.Integer(_('# Days by Employer'), default = 0)
    max_days = fields.Integer(_('Max # of days'))
    ceiling = fields.Integer(
        'Ceiling', default = 0, help = 'Expressed in months')
    ceiling_type = fields.Selection(
        [('min', 'Minimum Wage'), ('med', 'Medium Wage')],
        string = 'Ceiling based on')
    

class hr_holidays(models.Model):
    _inherit = 'hr.holidays'

    @api.one
    @api.onchange('holiday_status_id')
    def _get_sl(self):
        self.is_sick_leave = self.holiday_status_id.is_sick_leave
    
    @api.one
    @api.constrains('initial_id', 'diag_code')
    def _validate_sl(self):
        if self.is_sick_leave:
            # print self.diag_code, (int(self.diag_code) not in range(1000))
            if self.diag_code is not False:
                if not self.diag_code.isdigit():
                    raise ValidationError("Diagnostic Code must be a number")
                if int(self.diag_code) not in range(1000):
                    raise ValidationError("Diagnostic Code must be between 1-999")
            else:
                raise Warning("Set Diagnostic Code")
            if self.initial_id.date_to is not False and not \
                    (self.initial_id.date_to[:10] == self.date_from[:10] or \
                    (self.initial_id.holidays_status_id.id == self.holidays_status_id.id and 
                    self.diag_code == self.initial_id.diag_code)):
                raise ValidationError("Wrong Initial Sick Leave for type and Diagnostci Code")

    @api.one
    @api.depends('date_from','date_to', 'holiday_status_id')
    def _get_holiday_days(self):
        emp_days = 0
        comp_days = 0
        if self.is_sick_leave:
            if self.initial_id:
                emp_days += self.initial_id.number_of_days_temp
            if emp_days <= self.holiday_status_id.employer_days:
                emp_days = self.holiday_status_id.employer_days - emp_days
        if self.number_of_days_temp <= emp_days:
            emp_days = self.number_of_days_temp
        comp_days = self.number_of_days_temp - emp_days
        self.employer_days = emp_days
        self.budget_days = comp_days

    @api.one
    @api.depends('date_from','date_to', 'holiday_status_id')
    def _get_holiday_daily_base(self):
        daily_base = 0
        if not self.is_unpaid:
            if self.is_sick_leave:
                if self.initial_id:
                    daily_base = self.initial_id.daily_base
                else:
                    daily_base = self.employee_id._get_holiday_base(date=self.date_from, month_no=6)
                    daily_base = daily_base * self.holiday_status_id.percentage / 100
                self.employer_amount = self.employer_days * daily_base
                self.budget_amount = self.budget_days * daily_base
                self.total_amount = self.number_of_days_temp * daily_base
            else:
                daily_base = self.employee_id._get_holiday_base(date=self.date_from, month_no=3)
        self.daily_base = daily_base

    is_sick_leave = fields.Boolean(
        related = 'holiday_status_id.is_sick_leave',
        readonly = True, store = True)
    is_unpaid = fields.Boolean(
        related = 'holiday_status_id.is_unpaid',
        readonly = True, store = True)
    diag_code = fields.Char('Diagnostic Code', copy = False)
    allowance_code = fields.Char(
        'Allowance Code', related = 'holiday_status_id.indemn_code',
        readonly=True, store = True)
    medical_emergency = fields.Boolean(
        'Medical Emergency', related = 'holiday_status_id.emergency',
        readonly=True, store = True)
    initial_id = fields.Many2one('hr.holidays', 'Initial Sick Leave', copy = False)    
    employer_days = fields.Integer(_('# Days by Employer'), compute='_get_holiday_days', store=True)
    budget_days = fields.Integer(_('# Days by Social Security'), compute='_get_holiday_days', store=True)
    daily_base = fields.Float(_('Daily Base'), compute='_get_holiday_daily_base', store=True)
    employer_amount = fields.Float(_('Amount by Employer'), compute='_get_holiday_daily_base', store=True)
    budget_amount = fields.Float(_('Amount by Social Sevcurity'), compute='_get_holiday_daily_base', store=True)
    total_amount = fields.Float(_('Total Amount'), compute='_get_holiday_daily_base', store=True)
