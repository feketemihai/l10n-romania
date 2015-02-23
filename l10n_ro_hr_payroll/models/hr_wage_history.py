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

class hr_wage_history(models.Model):
    _name = 'hr.wage.history'
    _description = 'Wage History'
    _rec_name = 'date'
    _order = 'date desc'
    _sql_constrains = [(
        'date_uniq',
        'unique (date)',
        'Unique date',
    )]

    date = fields.Date('Month/Year', required = True, index = True)
    min_wage = fields.Integer('Minimum Wage per economy', required = True)
    med_wage = fields.Integer('Medium Wage per economy', required = True)
    working_days = fields.Integer(
        'Number of Working(ed) Days', required = True)
    ceiling_min_wage = fields.Integer(
        'Ceiling for 6 month income', required = True)
