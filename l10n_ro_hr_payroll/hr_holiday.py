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
    ceiling = fields.Integer('Ceiling', default = 0, help = 'Expressed in months')
    ceiling_type = fields.Selection(('min', 'Minimum Wage'), ('med', 'Medium Wage'))
    zileang = fields.Integer('# Days by Employer', default = 0)


class hr_holidays_status(models.Model):
    _inherit = 'hr.holidays.status'

    @api.one
    @api.depends('name')
    def _compute_leave_code(self):
        leave_code = ''.join(x[0] for x in self.name.split()).upper()
        if self.status_type and leave_code == 'SL':
            leave_code += '-' + self.status_type.code
        self.leave_code = leave_code

    leave_code = fields.Char(
        'Leave Code', compute = '_compute_leave_code', store = True)

class hr_holidays(models.Model):
    _inherit = 'hr.holidays'

    @api.one
    @api.depends('holiday_status_id')
    @api.constrains('status_type')
    def _validate_status_type(self):
        if self.holiday_status_id:
            if not self.holiday_status_id.name.startswith('Sick'):
                raise ValidationError(_("Leave Code is only for Sick Leaves"))
        else:
            raise ValidationError(_("Set Leave Type first"))

    status_type = fields.Many2one(
        'hr.holidays.status.type', 'Leave Code', readonly=True,
        states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]})

class hr_holidays_line(models.Model):
    _inherit = 'hr.holidays.public.line'

    # override - pentru a sterge intrarile daca s-a sters vacanta publica
    holidays_id = fields.Many2one('hr.holidays.public',
                                  'Holiday Calendar Year',
                                  ondelete = 'cascade')

class hr_public_holidays(models.Model):
    _inherit = 'hr.holidays.public'

    category_id = fields.Many2one(
        'hr.employee.category', string = 'Employee Tag', required = True)
    holiday_status_id = fields.Many2one(
        'hr.holidays.status', string = 'Leave Type', required = True)
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('approve', 'Approved'),
            ('decline', 'Declined'),
            ('close', 'Closed'),
        ], default = 'draft'
    )

    @api.one
    def state_approve(self):
        print self.state
        self.state = 'approve'
        print self.state
        return True

    @api.one
    def state_decline(self):
        print self.state
        self.state = 'decline'
        print self.state
        return True

    @api.one
    def set_to_draft(self):
        self.state = 'draft'
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_delete(
            self.env.user.id, 'hr.holidays.public', self.id, self.env.cr)
        wf_service.trg_create(
            self.env.user.id, 'hr.holidays.public', self.id, self.env.cr)
        return True

    def state_close(self):
        return self.create_leave_reqs()

    @api.one
    def create_leave_reqs(self):
        '''
        First it creates an approved allocation request for all the public
        holidays.
        Second stage creates an approved leave request for each day.
        '''
        allocation_req = self.pool.get('hr.holidays')
        values = {
            'name': 'Alocare Zile Libere Legale pt Anul %s' % self.year,
            'state': 'confirm',
            'holiday_status_id': self.holiday_status_id.id,
            'number_of_days_temp': len(self.line_ids),
            'category_id': self.category_id.id,
            'holiday_type': 'category',
            'type': 'add',
            'user_id': None,
            'employee_id': None,
        }
        alloc_id = allocation_req.create(self.env.cr, self.env.user.id, values)
        ret = allocation_req.holidays_validate(
            self.env.cr, self.env.user.id, [alloc_id])
        if ret is False:
            return False

        values['type'] = 'remove'
        values['number_of_days_temp'] = 1
        leave_ids = []
        for line in self.line_ids:
            date_from = fields.Datetime.from_string(line.date)
            values['name'] = line.name
            # de la data 00:00:00
            values['date_from'] = fields.Datetime.to_string(date_from)
            # pana la data 23:59:59
            values['date_to'] = fields.Datetime.to_string(
                date_from+timedelta(seconds=86399))
            leave_ids.append(
                allocation_req.create(self.env.cr, self.env.user.id, values))
        ret = allocation_req.holidays_validate(
            self.env.cr, self.env.user.id, leave_ids)
        if ret is False:
            return False
        self.state = 'close'
        return True