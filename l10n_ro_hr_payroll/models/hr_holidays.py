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
        if self.is_sick_leave:
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
            if not self.employer_days:
                raise ValidationError(_('Set # of Days by Employer'))
            if not self.max_days:
                raise ValidationError(_('Set Maximum # of Days'))

    leave_code = fields.Char(
        'Leave Code', compute = '_compute_leave_code', store = True)

    is_sick_leave = fields.Boolean(_('Is Sick Leave'), default = False)
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
    @api.constrains('initial_id', 'diag_code')
    def _validate_sl(self):
        if self.is_sick_leave:
            print self.diag_code, (int(self.diag_code) not in range(1, 1000))
            if self.diag_code is not False:
                if not self.diag_code.isdigit():
                    raise ValidationError("Diagnostic Code must be a number")
                if int(self.diag_code) not in range(1000):
                    raise ValidationError("Diagnostic Code must be between 1-999")
            else:
                raise Warning("Set Diagnostic Code")
            if self.initial_id.date_to is not False and not (self.initial_id.date_to[:10] == self.date_from[:10] or self.diag_code == self.initial_id.diag_code):
                raise ValidationError("Wrong Initial Sick Leave")

    is_sick_leave = fields.Boolean(
        related = 'holiday_status_id.is_sick_leave', store = True)
    diag_code = fields.Char('Diagnostic Code')
    allowance_code = fields.Char(
        'Allowance Code', related = 'holiday_status_id.indemn_code',
        readonly=True, store = True)
    medical_emergency = fields.Boolean(
        'Medical Emergency', related = 'holiday_status_id.emergency',
        readonly=True, store = True)
    initial_id = fields.Many2one('hr.holidays', 'Initial Sick Leave')

    @api.model
    def _create_resource_leave(self, leaves):
        '''This method will create entry in resource calendar leave object at the time of holidays validated '''
        obj_res_leave = self.env['resource.calendar.leaves']
        for leave in leaves:
            # from utc to user's tz
            date_from = fields.Datetime.context_timestamp(
                leave, datetime.strptime(leave.date_from,
                tools.DEFAULT_SERVER_DATETIME_FORMAT)).strftime(
                tools.DEFAULT_SERVER_DATETIME_FORMAT)
                
            date_to = fields.Datetime.context_timestamp(
                leave, datetime.strptime(leave.date_to,
                tools.DEFAULT_SERVER_DATETIME_FORMAT)).strftime(
                tools.DEFAULT_SERVER_DATETIME_FORMAT)

            vals = {
                'name': leave.name,
                'date_from': date_from,
                'holiday_id': leave.id,
                'date_to': date_to,
                'resource_id': leave.employee_id.resource_id.id,
                'calendar_id': leave.employee_id.resource_id.calendar_id.id
            }
            obj_res_leave.create(vals)
        return True
