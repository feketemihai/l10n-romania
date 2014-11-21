# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Fekete Mihai <mihai.fekete@forbiom.eu>
#    Copyright (C) 2014 FOREST AND BIOMASS SERVICES ROMANIA SA (http://www.forbiom.eu).
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

from openerp import models, fields, api

# fields copy if 'use_parent_address' is checked
ADDRESS_FIELDS = ('street', 'street2', 'zip', 'city', 'city_id', 'commune_id', 'state_id', 'zone_id', 'country_id')

class res_partner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"
    
    @api.onchange('city_id')
    def _onchange_city_id(self):
        if self.city_id:
            self.commune_id = self.city_id.commune_id.id
            self.state_id = self.city_id.state_id.id
            self.zone_id = self.city_id.zone_id.id
            self.country_id = self.city_id.country_id.id
            
    @api.onchange('commune_id')
    def _onchange_commune_id(self):
        if self.commune_id:
            self.city_id = False
            self.state_id = self.commune_id.state_id.id
            self.zone_id = self.commune_id.zone_id.id
            self.country_id = self.commune_id.country_id.id
            
    @api.onchange('state_id')
    def _onchange_state_id(self):
        if self.state_id:
            self.city_id = False
            self.commune_id = False
            self.zone_id = self.state_id.zone_id.id
            self.country_id = self.state_id.country_id.id
    
    @api.onchange('zone_id')
    def _onchange_zone_id(self):
        if self.zone_id:
            self.city_id = False
            self.commune_id = False
            self.state_id = False
            self.country_id = self.zone_id.country_id.id
    
    city_id = fields.Many2one('res.country.city', string='City', ondelete='set null', index=True)
    city = fields.Char(related='city_id.name', string='City', store=True)
    commune_id = fields.Many2one('res.country.commune', string='City/Commune', ondelete='set null', index=True)
    zone_id = fields.Many2one('res.country.zone', string='Zone', ondelete='set null', index=True)

    @api.one
    def _address_fields(self):
        """ Returns the list of address fields that are synced from the parent
        when the `use_parent_address` flag is set. """
        return list(ADDRESS_FIELDS)

    
