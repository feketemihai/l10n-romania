# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Deltatech All Rights Reserved
#                    Dorin Hongu <dhongu(@)gmail(.)com       
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from odoo import models, fields, api


class res_currency(models.Model):
    _inherit = 'res.currency'

    rate_inv = fields.Float( string='Inverse Rate',   compute="_compute_rate_inv", digits=(12, 4) )



    @api.depends('rate')
    def _compute_rate_inv(self):
        for currency in self:
            if currency.rate != 0:
                currency.rate_inv = 1 / currency.rate
            else:
                currency.rate_inv = 0



class res_currency_rate(models.Model):
    _inherit = 'res.currency.rate' 

    rate_inv = fields.Float( string='Inverse Rate',   compute="_compute_rate_inv", digits=(12, 4) )



    @api.depends('rate')
    def _compute_rate_inv(self):
        for currency in self:
            if currency.rate != 0:
                currency.rate_inv = 1 / currency.rate
            else:
                currency.rate_inv = 0