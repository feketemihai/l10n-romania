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

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

import simplejson
import urllib2

htmlcodes = ['&Aacute;', '&aacute;', '&Agrave;', '&Acirc;', '&agrave;', '&Acirc;', '&acirc;', '&Auml;', '&auml;', '&Atilde;', '&atilde;', '&Aring;', '&aring;', '&Aelig;', '&aelig;', '&Ccedil;', '&ccedil;', '&Eth;', '&eth;', '&Eacute;', '&eacute;', '&Egrave;', '&egrave;', '&Ecirc;', '&ecirc;', '&Euml;', '&euml;', '&Iacute;', '&iacute;', '&Igrave;', '&igrave;', '&Icirc;', '&icirc;', '&Iuml;', '&iuml;', '&Ntilde;', '&ntilde;', '&Oacute;', '&oacute;', '&Ograve;', '&ograve;', '&Ocirc;', '&ocirc;', '&Ouml;', '&ouml;', '&Otilde;', '&otilde;', '&Oslash;', '&oslash;', '&szlig;', '&Thorn;', '&thorn;', '&Uacute;', '&uacute;', '&Ugrave;', '&ugrave;', '&Ucirc;', '&ucirc;', '&Uuml;', '&uuml;', '&Yacute;', '&yacute;', '&yuml;', '&copy;', '&reg;', '&trade;', '&euro;', '&cent;', '&pound;', '&lsquo;', '&rsquo;', '&ldquo;', '&rdquo;', '&laquo;', '&raquo;', '&mdash;', '&ndash;', '&deg;', '&plusmn;', '&frac14;', '&frac12;', '&frac34;', '&times;', '&divide;', '&alpha;', '&beta;', '&infin']
funnychars = ['\xc1','\xe1','\xc0','\xc2','\xe0','\xc2','\xe2','\xc4','\xe4','\xc3','\xe3','\xc5','\xe5','\xc6','\xe6','\xc7','\xe7','\xd0','\xf0','\xc9','\xe9','\xc8','\xe8','\xca','\xea','\xcb','\xeb','\xcd','\xed','\xcc','\xec','\xce','\xee','\xcf','\xef','\xd1','\xf1','\xd3','\xf3','\xd2','\xf2','\xd4','\xf4','\xd6','\xf6','\xd5','\xf5','\xd8','\xf8','\xdf','\xde','\xfe','\xda','\xfa','\xd9','\xf9','\xdb','\xfb','\xdc','\xfc','\xdd','\xfd','\xff','\xa9','\xae','\u2122','\u20ac','\xa2','\xa3','\u2018','\u2019','\u201c','\u201d','\xab','\xbb','\u2014','\u2013','\xb0','\xb1','\xbc','\xbd','\xbe','\xd7','\xf7','\u03b1','\u03b2','\u221e']

       
def str_conv(textcontent):
    newtext = ''
    for char in textcontent:
        if char not in funnychars:
            newtext = newtext + char
        else:
            newtext = newtext + htmlcodes[funnychars.index(char)]
    return newtext
    
class res_country_zipcode(models.Model):
    _name = 'res.country.zipcode'
    _description = 'Zipcodes'
    
    @api.multi
    def name_get(self):
        res = []
        for zipcode in self:
            res.append((zipcode.id, "%s %s %s %s" % (zipcode.zipcode, zipcode.name, zipcode.state_id and zipcode.state_id.name or '',zipcode.country_id and zipcode.country_id.name or '')))            
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('name', '=', name)] + args, limit=limit)
        if not recs:
            recs = self.search([('zipcode', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('descriere', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('state_id.name', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('country_id.name', operator, name)] + args, limit=limit)
        return recs.name_get()
        
    name = fields.Char('City', size=64, required=True, select=1)
    zipcode = fields.Char('ZIP', size=64, required=True, select=1)
    state_id = fields.Many2one('res.country.state', 'State', required=True, select=1)
    descriere = fields.Char('Descriere', required=True, select=1)
    country_id = fields.Many2one('res.country', related='state_id.country_id', string="Country")

class CountryState(models.Model):
    _name = 'res.country.state'
    _inherit = 'res.country.state'
    
    city_ids = fields.One2many('res.country.zipcode', 'state_id', string='Cities')


class res_partner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"
    
    location_id = fields.Many2one('res.country.zipcode', string='Location', ondelete='set null', index=True)

    @api.one
    def get_google_zip_from_reply(self, strict=True):
        google_url = 'http://maps.googleapis.com/maps/api/geocode/json?'        
        city_obj = self.env['res.country.zipcode']
        state_obj = self.env['res.country.state']
        country_obj = self.env['res.country']
        headers = {'COntent-Type': 'application/json'}
        data = None
        if self:
            part = self[0]
            found = False
            if part.zip:
                found = city_obj.search([('zipcode','=',part.zip)])
            if found:
                found = found[0]
                part.write({'location_id': found})
            else:
                address = 'address='.encode('utf-8')
                if part.street:
                    address += part.street.replace(' ','+').encode('utf-8') + '+'
                if part.street2:
                    address += part.street2.replace(' ','+').encode('utf-8') + '+'
                if part.city:
                    address += part.city.replace(' ','+').encode('utf-8') + '+'
                if part.state_id:
                    address += part.state_id.name.replace(' ','+').encode('utf-8') + '+'
                if part.zip:
                    address += part.zip.encode('utf-8') + '+'
                if part.country_id:
                    address += part.country_id.name.encode('utf-8')
                if address<>'address='.encode('utf-8'):
                    address += '&sensor=false&language=en'
                    try:
                        url = google_url + address
                        req = urllib2.Request(url, data, headers)
                        answer = urllib2.urlopen(req)
                        res = simplejson.load(answer)
                        if res and res['results']:
                            doc = res['results'][0] and res['results'][0]['address_components'] and res['results'][0]['address_components']
                            city = state = country = zip1 = desc = False
                            for line in doc:
                                if line['types']==['locality', 'political']:
                                    try:
                                        city = line['long_name'].decode('utf-8')
                                    except:
                                        city = str_conv(line['long_name'])
                                    if not state:
                                        try:
                                            state = line['long_name'].decode('utf-8').replace(' County','')
                                        except:
                                            state = str_conv(line['long_name']).replace(' County','')                                    
                                        try:
                                            state_code = line['short_name'].decode('utf-8')
                                        except:
                                            state_code = str_conv(line['short_name'])
                                if line['types']==['administrative_area_level_1', 'political']:                                    
                                    try:
                                        state = line['long_name'].decode('utf-8').replace(' County','')
                                    except:
                                        state = str_conv(line['long_name']).replace(' County','')                                    
                                    try:
                                        state_code = line['short_name'].decode('utf-8')
                                    except:
                                        state_code = str_conv(line['short_name'])              
                                if line['types']==['country', 'political']:
                                    try:
                                        country = line['long_name'].decode('utf-8')
                                    except:
                                        country = str_conv(line['long_name'])                                    
                                if line['types']==['postal_code']:
                                    try:
                                        zip1 = line['long_name'].decode('utf-8')
                                    except:
                                        zip1 = str_conv(line['long_name'])                                    
                                if line['types']==['route']:
                                    try:
                                        desc = line['long_name'].decode('utf-8') or part.street
                                    except:
                                        desc = str_conv(line['long_name']) or part.street
                                elif line['types']==['administrative_area_level_2', 'political']:
                                    try:
                                        desc = line['long_name'].decode('utf-8') or part.street
                                    except:
                                        desc = str_conv(line['long_name']) or part.street
                                elif line['types']==['establishment']:
                                    try:
                                        desc = line['long_name'].decode('utf-8') or part.street
                                    except:
                                        desc = str_conv(line['long_name']) or part.street               
                            if zip1 and country and state:
                                countries = country_obj.search([('name','=',country)])
                                if countries:
                                    country_id = countries[0]
                                    state_ids = state_obj.search([('name','=',state)])
                                    if state_ids:
                                        state_id = state_ids[0]
                                    else:
                                        state_id = state_obj.create({'name': state, 'code': state_code, 'country_id': country_id.id})      
                                    found = city_obj.search([('state_id','=',state_id.id),('country_id','=',country_id.id),('zipcode','=',zip1)])
                                    if found:
                                        found = found[0]
                                        part.write({'location_id': found.id})
                                    else:
                                        found = city_obj.create({'state_id': state_id.id, 'country_id': country_id.id, 'zipcode': zip1, 'name': city, 'descriere': desc })
                                        part.write({'location_id': found.id})
                    except Exception, exc:
                        if strict:
                            raise except_orm(_('Google Geocoding service not reachable.'), str(exc))
