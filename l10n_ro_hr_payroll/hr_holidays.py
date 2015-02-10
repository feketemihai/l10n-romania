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

from datetime import timedelta
from openerp import netsvc, models, fields, api, _
from openerp.exceptions import ValidationError


class hr_holidays_status_type(models.Model):
    _name = 'hr.holidays.status.type'
    _description = 'Leave status types'

    name = fields.Char('Name')
    code = fields.Char('Code', required = True)
    value = fields.Float('Percentage', decimal = (0,2), required = True)
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

    @api.one
    @api.depends('holiday_status_id')
    @api.constrains('status_type')
    def _validate_status_type(self):
        if self.holiday_status_id:
            sl = self.env.ref('hr_holidays.holiday_status_sl')
            print bool(sl.id == self.holiday_status_id.id)
            if not self.holiday_status_id.name.startswith('Sick'):
                raise ValidationError(_("Leave Code is only for Sick Leaves"))
        else:
            raise ValidationError(_("Set Leave Type first"))

    status_type = fields.Many2one(
        'hr.holidays.status.type', 'Sick Leave Code', readonly=True,
        states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]})

