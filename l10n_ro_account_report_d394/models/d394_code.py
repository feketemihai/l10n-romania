# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Fekete Mihai <mihai.fekete@forbiom.eu>
#    Copyright (C) 2014 FOREST AND BIOMASS SERVICES ROMANIA SA
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


class product_product(models.Model):
    _inherit = "product.product"

    d394_id = fields.Many2one('report.394.code', string='D394 codes')


class report_394_code(models.Model):
    _name = "report.394.code"
    _description = "D394 code"

    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _order = 'parent_left'

    _constraints = [
        (models.Model._check_recursion, 'Error ! You cannot create recursive codes.', ['parent_id'])
    ]

    name = fields.Char('D394 Code')
    parent_id = fields.Many2one('report.394.code', 'Parent Code', ondelete="restrict")
    child_ids = fields.One2many('report.394.code', 'parent_id', 'Child Codes')
    parent_left = fields.Integer('Left Parent', select=True)
    parent_right = fields.Integer('Rigth Parent', select=True)
    description = fields.Char('Description')
    product_ids = fields.One2many('product.product', 'd394_id', string='Products')
