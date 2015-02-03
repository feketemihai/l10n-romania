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
from openerp.exceptions import ValidationError


class hr_holidays_status_type(models.Model):
    _name = 'hr.holidays.status.type'
    _description = 'Leave status types'

    name = fields.Char('Name')
    code = fields.Char('Code', required = True)
    value = fields.Float('Percentage', decimal = (0,2), required = True)
    ceiling = fields.Integer('Ceiling', default = 0, help = 'Expressed in months')

class hr_holidays(models.Model):
    _inherit = 'hr.holidays'

    @api.one
    @api.depends('holiday_status_id')
    @api.constrains('status_type')
    def _validate_status_type(self):
        if self.holiday_status_id:
            if not self.holiday_status_id.name.startswith('Sick'):
                raise ValidationError(_("Leave Code is only for Sick Leaves"))

    status_type = fields.Many2one('hr.holidays.status.type', 'Leave Code', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]})
