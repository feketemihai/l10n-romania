#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

from openerp.osv import osv, fields
from openerp.osv.osv import except_osv
from openerp.tools.translate import _

import logging

import httplib, random, re, urllib
from BeautifulSoup import BeautifulSoup
import simplejson
from urllib import urlencode

import requests
from urllib2 import urlopen
logger = logging.getLogger('Google Zip search')

htmlcodes = ['&Aacute;', '&aacute;', '&Agrave;', '&Acirc;', '&agrave;', '&Acirc;', '&acirc;', '&Auml;', '&auml;', '&Atilde;', '&atilde;', '&Aring;', '&aring;', '&Aelig;', '&aelig;', '&Ccedil;', '&ccedil;', '&Eth;', '&eth;', '&Eacute;', '&eacute;', '&Egrave;', '&egrave;', '&Ecirc;', '&ecirc;', '&Euml;', '&euml;', '&Iacute;', '&iacute;', '&Igrave;', '&igrave;', '&Icirc;', '&icirc;', '&Iuml;', '&iuml;', '&Ntilde;', '&ntilde;', '&Oacute;', '&oacute;', '&Ograve;', '&ograve;', '&Ocirc;', '&ocirc;', '&Ouml;', '&ouml;', '&Otilde;', '&otilde;', '&Oslash;', '&oslash;', '&szlig;', '&Thorn;', '&thorn;', '&Uacute;', '&uacute;', '&Ugrave;', '&ugrave;', '&Ucirc;', '&ucirc;', '&Uuml;', '&uuml;', '&Yacute;', '&yacute;', '&yuml;', '&copy;', '&reg;', '&trade;', '&euro;', '&cent;', '&pound;', '&lsquo;', '&rsquo;', '&ldquo;', '&rdquo;', '&laquo;', '&raquo;', '&mdash;', '&ndash;', '&deg;', '&plusmn;', '&frac14;', '&frac12;', '&frac34;', '&times;', '&divide;', '&alpha;', '&beta;', '&infin']
funnychars = ['\xc1','\xe1','\xc0','\xc2','\xe0','\xc2','\xe2','\xc4','\xe4','\xc3','\xe3','\xc5','\xe5','\xc6','\xe6','\xc7','\xe7','\xd0','\xf0','\xc9','\xe9','\xc8','\xe8','\xca','\xea','\xcb','\xeb','\xcd','\xed','\xcc','\xec','\xce','\xee','\xcf','\xef','\xd1','\xf1','\xd3','\xf3','\xd2','\xf2','\xd4','\xf4','\xd6','\xf6','\xd5','\xf5','\xd8','\xf8','\xdf','\xde','\xfe','\xda','\xfa','\xd9','\xf9','\xdb','\xfb','\xdc','\xfc','\xdd','\xfd','\xff','\xa9','\xae','\u2122','\u20ac','\xa2','\xa3','\u2018','\u2019','\u201c','\u201d','\xab','\xbb','\u2014','\u2013','\xb0','\xb1','\xbc','\xbd','\xbe','\xd7','\xf7','\u03b1','\u03b2','\u221e']


def parseTable(html):
    #Each "row" of the HTML table will be a list, and the items
    #in that list will be the TD data items.
    ourTable = []

    #We keep these set to NONE when not actively building a
    #row of data or a data item.
    ourTD = None    #Stores one table data item
    ourTR = None    #List to store each of the TD items in.


    #State we keep track of
    inTable = False
    inTR = False
    inTD = False

    #Start looking for a start tag at the beginning!
    tagStart = html.find("<", 0)

    while( tagStart != -1):
        tagEnd = html.find(">", tagStart)

        if tagEnd == -1:    #We are done, return the data!
            return ourTable

        tagText = html[tagStart+1:tagEnd]

        #only look at the text immediately following the <
        tagList = tagText.split()
        tag = tagList[0]
        tag = tag.lower()

        #Watch out for TABLE (start/stop) tags!
        if tag == "table":      #We entered the table!
            inTable = True
        if tag == "/table":     #We exited a table.
            inTable = False

        #Detect/Handle Table Rows (TR's)
        if tag == "tr":
            inTR = True
            ourTR = []      #Started a new Table Row!

        #If we are at the end of a row, add the data we collected
        #so far to the main list of table data.
        if tag == "/tr":
            inTR = False
            ourTable.append(ourTR)
            ourTR = None

        #We are starting a Data item!
        if tag== "td":
            inTD = True
            ourTD = ""      #Start with an empty item!

        #We are ending a data item!
        if tag == "/td":
            inTD = False
            if ourTD != None and ourTR != None:
                cleanedTD = ourTD.strip()   #Remove extra spaces
                ourTR.append( ourTD.strip() )
            ourTD = None


        #Look for the NEXT start tag. Anything between the current
        #end tag and the next Start Tag is potential data!
        tagStart = html.find("<", tagEnd+1)

        #If we are in a Table, and in a Row and also in a TD,
        # Save anything that's not a tag! (between tags)
        #
        #Note that this may happen multiple times if the table
        #data has tags inside of it!
        #e.g. <td>some <b>bold</b> text</td>
        #
        #Because of this, we need to be sure to put a space between each
        #item that may have tags separating them. We remove any extra
        #spaces (above) before we append the ourTD data to the ourTR list.
        if inTable and inTR and inTD:
            ourTD = ourTD + html[tagEnd+1:tagStart] + " "
            #print("td:", ourTD)   #for debugging


    #If we end the while loop looking for the next start tag, we
    #are done, return ourTable of data.
    return ourTable

def getSomeData(method, action, params):
    req = requests.post(action, params=params)
    content = req.content
    data = content.replace("\t", "").replace("\r", "").replace("\n", "").replace("&nbsp;"," ")
    soup = BeautifulSoup(data)
    dataTable = parseTable(str(soup.findAll('div',attrs={'id':'main'})))
    return dataTable

def getMainData(cod):
    params = {'cod': cod, 'B1': 'VIZUALIZARE'}
    return getSomeData("POST", "http://www.mfinante.ro/infocodfiscal.html", params)

def getViesData(cc, vat):
    params = {
        "memberStateCode": cc.upper(),
        "number": vat,
        "traderName": "",
        "traderStreet": "",
        "traderPostalCode": "",
        "traderCity": "",
        "requesterMemberStateCode": cc.upper(),
        "requesterNumber": vat,
        "action": "check",
        "check": "Verify",
    }
    r = requests.get(VIES_RESPONSE, params=params)
    html_doc = lxml.html.fromstring(r.content)
    if u"Application unavailable" in r.content:
        raise Unavailable()
    info = {}
    errors = html_doc.cssselect("span.invalidStyle")

    if errors:
        for error in errors:
            if error.text:
                raise InvalidVATNumber(u"".join(error.itertext()))

    for tr in html_doc.cssselect("#vatResponseFormTable tr"):
        tds = list(tr.iterchildren())
        if len(tds) < 2:
            continue
        for td in tds:
            if td.get("class") == "labelStyle":
                key = td.text.strip()
            if td.text and td.text.strip() and key:
                info[key] = u"\n".join(t.strip() for t in td.itertext())
    return info
        
def str_conv(textcontent):
    newtext = ''
    for char in textcontent:
        if char not in funnychars:
            newtext = newtext + char
        else:
            newtext = newtext + htmlcodes[funnychars.index(char)]
    return newtext
    
class city(osv.osv):

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for line in self.browse(cr, uid, ids, context=context):
            name = line.name
            if line.zipcode:
                name = "%s %s" % (line.zipcode, name)
            if line.state_id:
                name = "%s, %s" % (name, line.state_id.name)
            if line.country_id:
                name = "%s, %s" % (name, line.country_id.name)
            res.append((line['id'], name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if args is None:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, uid, [('zipcode', 'ilike', name)]+ args, limit=limit)
        if not ids:
            ids = self.search(cr, uid, [('descriere', operator, name)]+ args, limit=limit)
        return self.name_get(cr, uid, ids, context=context)
        
    _name = 'city.city'
    _description = 'City'
    _columns = {
        'state_id': fields.many2one('res.country.state', 'State', required=True, select=1),
        'name': fields.char('City', size=64, required=True, select=1),
        'zipcode': fields.char('ZIP', size=64, required=True, select=1),
        'descriere': fields.char('Descriere', size=300, required=True, select=1),
        'country_id': fields.related('state_id', 'country_id', type="many2one",
                                     relation="res.country", string="Country",
                                     store=True),
    }
    def _default_country(self, cr, uid, context=None):
        if context is None:
            context = {}
        if 'country_id' in context and context['country_id']:
            return [context['category_id']]
        else:
            if 'state_id' in context and context['state_id']:
                return [context['state_id'].country_id]        
        return []
city()

class CountryState(osv.osv):
    _inherit = 'res.country.state'
    _columns = {
        'city_ids': fields.one2many('city.city', 'state_id', 'Cities'),
    }
CountryState()


class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'location_id': fields.many2one('city.city', 'Location', select=1),
        'zip': fields.related('location_id', 'zipcode', type="char", string="Zip",
                               store=True),
        'city': fields.related('location_id', 'name', type="char", string="City",
                               store=True),
        'state_id': fields.related('location_id', 'state_id', type="many2one",
                                   relation="res.country.state", string="State",
                                   store=True),
        'country_id': fields.related('location_id', 'country_id', type="many2one",
                                     relation="res.country", string="Country",
                                     store=True),
    }

    def get_google_zip_from_reply(self, cr, uid, partner, strict=True, context=None):
        """Parse geoname answer code inspired by geopy library"""

        google_url = 'http://maps.googleapis.com/maps/api/geocode/json?address='        
        city_obj = self.pool.get('city.city')
        state_obj = self.pool.get('res.country.state')
        country_obj = self.pool.get('res.country')
        if partner:
            part = self.browse(cr, uid, partner[0])
            if part:
                address = ''.encode('utf-8')
                if part.street:
                    address += part.street.replace(' ','+').encode('utf-8') + '+'
                if part.state_id:
                    address += part.state_id.name.replace(' ','+').encode('utf-8') + '+'
                if part.zip:
                    address += part.zip.encode('utf-8') + '+'
                if part.country_id:
                    address += part.country_id.name.encode('utf-8')
                if address<>''.encode('utf-8'):
                    address += '&sensor=false'
                    try:
                        url = google_url + address
                        answer = urlopen(url)
                        res = simplejson.load(answer)
                        if res and res['results']:
                            doc = res['results'][0]['address_components']
                            city = state = country = zip1 = desc = False
                            for line in doc:
                                if line['types']==['locality', 'political']:
                                    try:
                                        city = line['long_name'].decode('utf-8')
                                    except:
                                        city = str_conv(line['long_name'])
                                if line['types']==['administrative_area_level_1', 'political']:                                    
                                    try:
                                        state = line['long_name'].decode('utf-8')
                                    except:
                                        state = str_conv(line['long_name'])                                    
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
                                if zip1 and country and state:
                                    country = country_obj.search(cr, uid, [('name','=',country)])
                                    if country:
                                        country = country[0]
                                        state_id = state_obj.search(cr, uid, [('name','=',state)])
                                        if state_id:
                                            state_id = state_id[0]
                                        else:
                                            state_id = state_obj.create(cr, uid, {'name': state, 'code': state_code, 'country_id': country})        
                                        found = city_obj.search(cr, uid, [('state_id','=',state_id),('country_id','=',country),('zipcode','=',zip1)])
                                        if found:
                                            found = found[0]
                                            self.write(cr, uid, [part.id], {'location_id': found})
                                        else:
                                            found = city_obj.create(cr, uid, {'state_id': state_id, 'country_id': country, 'zipcode': zip1, 'name': city, 'descriere': desc })                                        
                                            self.write(cr, uid, [part.id], {'location_id': found})
                    except Exception, exc:
                        logger.exception('error while searching zip code')
                        if strict:
                            raise except_osv(_('Zip search fails'), str(exc))
        return True
        
    def _get_partner_data_one(self, cr, uid, partner, context=None):
        part = self.browse(cr, uid, partner, context=context)
        if part.vat:
            self.write(cr, uid, partner, {'vat': part.vat.upper().replace(" ","")})
        zips = self.pool.get('city.city')
        vat_number = vat_country = False
        if part.vat:
            vat_country, vat_number = self._split_vat(part.vat)                
        if part.vat_subjected:
            self.write(cr, uid, [part.id], {'vat_subjected': False})
        if vat_number and vat_country:
            if vat_country=='ro':
                try:
                    dataTable = getMainData(vat_number)
                    if dataTable:
                        for dict1 in dataTable:
                            if 'Denumire platitor:' in dict1:
                                nume = dict1[1] or ''
                            if 'Adresa:' in dict1:
                                adresa = dict1[1] or ''
                            if 'Numar de inmatriculare la RegistrulComertului:' in dict1:
                                if dict1[1]=='-/-/-':
                                    nrc = False
                                else:
                                    nrc = dict1[1].replace(' ','') or ''
                            if 'Codul postal:' in dict1:
                                zip1 = dict1[1] or ''
                            if 'Judetul:' in dict1:
                                if dict1[1]:
                                    state = self.pool.get('res.country.state').search(cr, uid, [('name','=',dict1[1].decode('utf-8').title())])
                                    if state:
                                        state = state[0]
                                    else:
                                        state = False
                                else:
                                    state = False
                            if 'Telefon:' in dict1:
                                tel = dict1[1] or ''
                            if 'Fax:' in dict1:
                                fax = dict1[1] or ''
                            if 'Taxa pe valoarea adaugata (data luarii in evidenta):' in dict1:
                                if dict1[1].replace(" ", "")<>'NU':
                                    vat_s = True                                    
                                else:    
                                    vat_s = False
                        if zip1:
                            zip2 = zips.search(cr, uid, [('zipcode','=',zip1)])
                            if zip2:
                                vals = {
                                    'street': adresa.decode('utf-8').title(),
                                    'phone': tel, 
                                    'fax': fax,
                                    'location_id': zip2[0]
                                }
                                self.write(cr, uid, [part.id], vals)
                        if not part.street:
                            vals = {
                            'street': adresa.decode('utf-8').title(),
                            'phone': tel, 
                            'fax': fax,
                            'zip': zip1,
                            'state_id': state,
                            'country_id': self.pool.get('res.country').search(cr, uid, [('code','=','RO')])[0]
                            }
                            self.write(cr, uid, [part.id], vals)                    
                            
                        self.write(cr, uid, [part.id], {'name': nume.decode('utf-8').upper(), 'is_company': True, 'nrc': nrc, 'vat_subjected': vat_s})
                except:
                    print 'Cannot connect to mfinante.ro'
            else:
                try:
                    dataTable = getViesData(vat_country.upper(), vat_number)
                    if dataTable:
                        if dataTable['Name'] and dataTable['Name']<>'---':
                            try:
                                self.write(cr, uid, [part.id], {'name': dataTable['Name'].decode('utf-8').upper(), 'is_company': True, 'vat_subjected':  True})
                            except:
                                self.write(cr, uid, [part.id], {'name': str_conv(dataTable['Name']).upper(), 'is_company': True, 'vat_subjected':  True})
                        if not part.street:
                            if dataTable['Address'] and dataTable['Address']<>'---':
                                try:
                                    self.write(cr, uid, [part.id], {'street': dataTable['Address'].decode('utf-8').upper()})
                                except:
                                    self.write(cr, uid, [part.id], {'street': str_conv(dataTable['Address']).upper()})
                                self.pool.get('city.city').get_google_zip_from_reply(cr, uid, [part.id], context=context)
                        self.write(cr, uid, [part.id], {'vat_subjected': self.vies_vat_check(cr, uid, vat_country, vat_number, context=context)})
                except:
                    self.write(cr, uid, [part.id], {'vat_subjected': self.vies_vat_check(cr, uid, vat_country, vat_number, context=context)})
        return True
res_partner()
