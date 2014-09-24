# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#	 TOTAL PC SYSTEMS
#    Copyright (C) 2011 (<http://www.erpsystems.ro>). All Rights Reserved
#    $Id$
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

from openerp.osv import fields, osv

class crm_lead(osv.osv):
    _inherit = 'crm.lead'

    _columns = {
        'location_id': fields.many2one('city.city', 'Location', select=1),
        'zip': fields.related('location_id', 'zipcode', type="char", string="Zip",
                               store=False),
        'city': fields.related('location_id', 'name', type="char", string="City",
                               store=False),
        'state_id': fields.related('location_id', 'state_id', type="many2one",
                                   relation="res.country.state", string="State",
                                   store=False),
        'country_id': fields.related('location_id', 'country_id', type="many2one",
                                     relation="res.country", string="Country",
                                     store=True),
    }
crm_lead()
