# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Fekete Mihai <mihai.fekete@forbiom.eu>
#    Copyright (C) 2016 FOREST AND BIOMASS SERVICES ROMANIA SA
#    (http://www.forbiom.eu).
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

from openerp import models, fields

SEQUENCE_TYPE = [
    ('normal', 'Invoice'),
    ('autoinv1', 'Customer Auto Invoicing'),
    ('autoinv2', 'Supplier  Auto Invoicing')
]


class IRSequence(models.Model):
    _inherit = 'ir.sequence'

    sequence_type = fields.Selection(SEQUENCE_TYPE, default='normal')
    number_first = fields.Integer('Serie First Number')
    number_last = fields.Integer('Serie Last Number')
    partner_id = fields.Many2one('res.partner', 'Partner')
    
