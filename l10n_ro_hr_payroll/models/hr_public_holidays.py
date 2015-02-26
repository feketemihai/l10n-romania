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
import pytz
from openerp import netsvc, models, fields, api, _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATEFORMAT

class hr_holidays_line(models.Model):
    _inherit = 'hr.holidays.public.line'

    alloc = fields.Many2one('hr.holidays')
    # override - pentru a sterge intrarile daca s-a sters vacanta publica
    holidays_id = fields.Many2one('hr.holidays.public',
                                  'Holiday Calendar Year',
                                  ondelete = 'cascade')

    @property
    def date_from_dt(self):
        return datetime.strptime(self.date[:10] + ' 00:00:00', DATEFORMAT)

    @property
    def date_to_dt(self):
        return datetime.strptime(self.date[:10] + ' 23:59:59', DATEFORMAT)

class hr_public_holidays(models.Model):
    _inherit = 'hr.holidays.public'

    category_id = fields.Many2one(
        'hr.employee.category', string = 'Employee Tag', required = True)
    holiday_status_id = fields.Many2one(
        'hr.holidays.status', string = 'Leave Type', required = True)
    master_alloc = fields.Many2one('hr.holidays')
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
        self.state = 'approve'
        return True

    @api.one
    def state_decline(self):
        self.state = 'decline'
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

    @api.one
    def state_close(self):
        return self.create_leave_reqs()

    def get_tz(self, env):
        tz_name = env.context.get('tz') or env.user.tz
        return tz_name and pytz.timezone(tz_name) or pytz.utc

    def dt_to_utc(self, tz, dt):
        return pytz.utc.normalize(
            tz.localize(dt, is_dst = False), is_dst = False)

    def dt_to_tz(self, tz, dt):
        return tz.normalize(
            pytz.utc.localize(dt, is_dst = False), is_dst = False)
     
    @api.one
    def create_employee_leave_reqs(self, employee_id):
        hol_obj = self.env['hr.holidays']
        if self.master_alloc.id is False:
            return False

        tz = self.get_tz(self.env)

        for line in self.line_ids:
            if line.alloc.id is False:
                continue
            date_from = self.dt_to_utc(tz, line.date_from_dt)
            date_to = self.dt_to_utc(tz, line.date_to_dt)
            
            alloc_id = hol_obj.search_count([
                ('employee_id', '=', employee_id),
                ('parent_id', '=', line.alloc.id),
                ('date_from', '=', str(date_from)),
                ('date_to', '=', str(date_to)),
            ])
            # skip, already allocated public holiday
            if alloc_id:
                continue

            values = {
                'name': line.name,
                'holiday_status_id': self.holiday_status_id.id,
                'holiday_type': 'employee',
                'type': 'remove',
                'employee_id': employee_id,
                'parent_id': line.alloc.id,
                'date_from': date_from,
                'date_to': date_to,
                'number_of_days_temp': 1,                
            }
            
            alloc_id = hol_obj.create(values)
            if alloc_id:
                for sig in ('confirm', 'validate', 'second_validate'):
                    hol_obj.signal_workflow(cr, uid, [alloc_id], sig)

        return True

    @api.one
    def allocate(self):
        if self.master_alloc.id:
            return self.master_alloc.id
        hol_obj = self.env['hr.holidays']
        values = {
            'name': _('%s for %s') % (self.holiday_status_id.name, self.year),
            'holiday_status_id': self.holiday_status_id.id,
            'number_of_days_temp': len(self.line_ids),
            'category_id': self.category_id.id,
            'holiday_type': 'category',
            'type': 'add',
            'employee_id': None,
        }

        self.master_alloc = hol_obj.create(values)
        if not self.master_alloc.id:
            return []

        for sig in ('confirm', 'validate', 'second_validate'):
            self.master_alloc.signal_workflow(sig)

        alloc = hol_obj.search([('parent_id', '=', self.master_alloc.id)])
        if len(alloc):
            # a mai fost alocata
            e_ids = set([a.employee_id.id for a in alloc])
            c_e_ids = set([e.id for e in self.category_id.employee_ids])
            ids = list(c_e_ids - e_ids)
        else:
            ids = [e.id for e in self.category_id.employee_ids]

        values = {
            'name': _('%s for %s') % (self.holiday_status_id.name, self.year),
            'holiday_status_id': self.holiday_status_id.id,
            'number_of_days_temp': len(self.line_ids),
            'holiday_type': 'employee',
            'type': u'add',
            'employee_id': None,
            'parent_id': self.master_alloc.id,
        }
        for emp_id in ids:
            values['employee_id'] = emp_id
            leave = hol_obj.create(values)
            for sig in ('confirm', 'validate', 'second_validate'):
                leave.signal_workflow(sig)
        return self.master_alloc.id

    @api.one
    def allocate_leaves(self):
        hol_obj = self.env['hr.holidays']
        tz = self.get_tz(self.env)
        for line in self.line_ids:
            values = {
                'name': line.name,
                'holiday_status_id': self.holiday_status_id.id,
                'number_of_days_temp': 1,
                'category_id': self.category_id.id,
                'type': 'remove',
                # de la data 00:00:00
                'date_from': self.dt_to_utc(tz, line.date_from_dt),
                # pana la data 23:59:59
                'date_to': self.dt_to_utc(tz, line.date_to_dt),
            }
            if line.alloc.id is False:
                values['holiday_type'] = 'category'
                values['employee_id'] = None
                line.alloc = hol_obj.create(values)
                for sig in ('confirm', 'validate', 'second_validate'):
                    line.alloc.signal_workflow(sig)
            alloc = hol_obj.search([('parent_id', '=', line.alloc.id)])
            if len(alloc):
                # a mai fost alocata
                e_ids = set([a.employee_id.id for a in alloc])
                c_e_ids = set([e.id for e in self.category_id.employee_ids])
                ids = list(c_e_ids - e_ids)
            else:
                ids = [e.id for e in self.category_id.employee_ids]
            values['holiday_type'] = 'employee'
            for emp_id in ids:
                values['employee_id'] = emp_id
                leave = hol_obj.create(values)
                for sig in ('confirm', 'validate', 'second_validate'):
                    leave.signal_workflow(sig)
            
                
    @api.one
    def create_leave_reqs(self):
        '''
        First it creates an approved allocation request for all the public
        holidays.
        Second stage creates an approved leave request for each day.
        '''
        self.allocate()
        self.allocate_leaves()
        self.state = 'close'
        return True
