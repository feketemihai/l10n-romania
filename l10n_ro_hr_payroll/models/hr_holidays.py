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


class hr_holidays_status_type(models.Model):
    _name = 'hr.holidays.status.type'
    _description = 'hr_holidays_status_type'

    name = fields.Char('Name')
    code = fields.Char('Allowance Code', required = True)
    emergency = fields.Boolean('Medical emergency', default = False)
    value = fields.Integer('Percentage')
    ceiling = fields.Integer(
        'Ceiling', default = 0, help = 'Expressed in months')
    ceiling_type = fields.Selection(
        [('min', 'Minimum Wage'), ('med', 'Medium Wage')],
        string = 'Ceiling based on')
    employer_days = fields.Integer('# Days by Employer', default = 0)
    max_days = fields.Integer('Max # of days')


class hr_holidays_status(models.Model):
    _inherit = 'hr.holidays.status'

    @api.one
    @api.depends('name')
    def _compute_leave_code(self):
        self.leave_code = ''.join(x[0] for x in self.name.split()).upper()

    leave_code = fields.Char(
        'Leave Code', compute = '_compute_leave_code', store = True)

class hr_holidays(models.Model):
    _inherit = 'hr.holidays'
# ???
    # @api.one
    # @api.onchange('holiday_status_id')
    # @api.constrains('holiday_status_id')
    # def _validate_status(self):
    #     if self.holiday_status_id:
    #         if self.env.ref('hr_holidays.holiday_status_sl').id == self.holiday_status_id.id:
    #             if self.status_type.name is False:
    #                 raise Warning(_("Set Sick Leave Code"))

    @property
    def _sick_leave(self):
        return self.env.ref('hr_holidays.holiday_status_sl')

    @property
    def _is_sick_leave(self):
        if self.holiday_status_id and self.holiday_status_id.id:
            return bool(self._sick_leave.id == self.holiday_status_id.id)
        return False

    # @api.one
    # @api.depends(('holiday_status_id', 'status_type'))
    # @api.constrains('status_type')
    # def _validate_status_type(self):
    #     if self.status_type:
    #         if self.env.ref('hr_holidays.holiday_status_sl').id != self.holiday_status_id.id:
    #             raise ValidationError(_("Sick Leave Code is only for Sick Leaves"))

    @api.one
    @api.onchange('holiday_status_id')
    def _compute_is_sick_leave(self):
        self.is_sick_leave = (self._sick_leave.id == self.holiday_status_id.id)

    @api.one
    @api.depends('holiday_status_id', 'status_type')
    @api.constrains('status_type', 'initial_id', 'allowance_code', 'diag_code')
    def _validate_sl(self):
        if self._sick_leave.id == self.holiday_status_id.id:
            print self.diag_code, (int(self.diag_code) not in range(1, 1000))
            if self.diag_code is not False:
                if not self.diag_code.isdigit():
                    raise ValidationError("Diagnostic Code must be a number")
                if int(self.diag_code) not in range(1000):
                    raise ValidationError("Diagnostic Code must be between 1-999")
            else:
                raise Warning("Set Diagnostic Code")
            if self.status_type.name is False:
                raise ValidationError("Set Sick Leave Status Type")
            if self.initial_id.date_to is not False and not (self.initial_id.date_to[:10] == self.date_from[:10] or self.diag_code == self.initial_id.diag_code):
                raise ValidationError("Wrong Initial Sick Leave")

    is_sick_leave = fields.Boolean(compute = '_compute_is_sick_leave', store = True)
    status_type = fields.Many2one(
        'hr.holidays.status.type', 'Sick Leave Code', readonly=True,
        states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]})
    diag_code = fields.Char('Diagnostic Code')
    allowance_code = fields.Char('Allowance Code', related = 'status_type.code', readonly=True)
    medical_emergency = fields.Boolean('Medical Emergency', related = 'status_type.emergency')
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
