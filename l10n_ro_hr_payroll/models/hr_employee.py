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

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    def get_company_tax(self, code):
        if self.company_id and self.company_id.name:
            return self.company_id.get_tax(code) or 0.0
        return 0.0


    def _get_payslips(self, limit = None):
        return self.env['hr.payslip'].search(
            [('employee_id', '=', employee_id), ('state', '=', 'done')])

    def bazacm(self):
        pass