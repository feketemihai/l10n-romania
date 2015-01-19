# -*- encoding: utf-8 -*-
##############################################################################
#
#	 Romanian accounting localization for OpenERP V7
#		@author -  Fekete Mihai, Tatár Attila <atta@nvm.ro>
#	 Copyright (C) 2011-2013 TOTAL PC SYSTEMS (http://www.www.erpsystems.ro). 
#	 Copyright (C) 2013 Tatár Attila
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import datetime
import time

from openerp import models, fields, api, _
from openerp.exceptions import Warning

import urllib
import lxml.html
import requests
import json
from BeautifulSoup import BeautifulSoup


htmlcodes = ['&Aacute;', '&aacute;', '&Agrave;', '&Acirc;', '&agrave;', '&Acirc;', '&acirc;', '&Auml;', '&auml;', '&Atilde;', '&atilde;', '&Aring;', '&aring;', '&Aelig;', '&aelig;', '&Ccedil;', '&ccedil;', '&Eth;', '&eth;', '&Eacute;', '&eacute;', '&Egrave;', '&egrave;', '&Ecirc;', '&ecirc;', '&Euml;', '&euml;', '&Iacute;', '&iacute;', '&Igrave;', '&igrave;', '&Icirc;', '&icirc;', '&Iuml;', '&iuml;', '&Ntilde;', '&ntilde;', '&Oacute;', '&oacute;', '&Ograve;', '&ograve;', '&Ocirc;', '&ocirc;', '&Ouml;', '&ouml;', '&Otilde;', '&otilde;', '&Oslash;', '&oslash;', '&szlig;', '&Thorn;', '&thorn;', '&Uacute;', '&uacute;', '&Ugrave;', '&ugrave;', '&Ucirc;', '&ucirc;', '&Uuml;', '&uuml;', '&Yacute;', '&yacute;', '&yuml;', '&copy;', '&reg;', '&trade;', '&euro;', '&cent;', '&pound;', '&lsquo;', '&rsquo;', '&ldquo;', '&rdquo;', '&laquo;', '&raquo;', '&mdash;', '&ndash;', '&deg;', '&plusmn;', '&frac14;', '&frac12;', '&frac34;', '&times;', '&divide;', '&alpha;', '&beta;', '&infin']
funnychars = ['\xc1','\xe1','\xc0','\xc2','\xe0','\xc2','\xe2','\xc4','\xe4','\xc3','\xe3','\xc5','\xe5','\xc6','\xe6','\xc7','\xe7','\xd0','\xf0','\xc9','\xe9','\xc8','\xe8','\xca','\xea','\xcb','\xeb','\xcd','\xed','\xcc','\xec','\xce','\xee','\xcf','\xef','\xd1','\xf1','\xd3','\xf3','\xd2','\xf2','\xd4','\xf4','\xd6','\xf6','\xd5','\xf5','\xd8','\xf8','\xdf','\xde','\xfe','\xda','\xfa','\xd9','\xf9','\xdb','\xfb','\xdc','\xfc','\xdd','\xfd','\xff','\xa9','\xae','\u2122','\u20ac','\xa2','\xa3','\u2018','\u2019','\u201c','\u201d','\xab','\xbb','\u2014','\u2013','\xb0','\xb1','\xbc','\xbd','\xbe','\xd7','\xf7','\u03b1','\u03b2','\u221e']

def str_conv(textcontent):
    newtext = ''
    for char in textcontent:
        if char not in funnychars:
            newtext = newtext + char
        else:
            newtext  = newtext + htmlcodes[funnychars.index(char)]
    return newtext
    
VIES_RESPONSE = "http://ec.europa.eu/taxation_customs/vies/vatResponse.html"

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


    #If we end the while loop looking for the next start tag, we
    #are done, return ourTable of data.
    return ourTable

def getMfinDryscape(cod):
    import dryscape

    sess = dryscape.Session(base_url = 'http://www.mfinante.ro/')
    sess.visit('/infocodfiscal.html')
    input_cod = sess.at_xpath("//form[@name='codfiscalForm']//input[@name='cod']")
    input_cod.set(cod)
    input_cod.form().submit()
    table = sess.at_xpath("//div[@id='main']//center/table")
    result = dict()
    for line in tab.text().decode('utf8').replace(u'\xa0', '').split('\n'):
       line = line.split('\t')
       result[line[0].strip()] = line[1].strip()
    return result
   
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
    req = requests.get(VIES_RESPONSE, params=params)
    content = req.content
    data = content.replace("\t", "").replace("\r", "").replace("\n", "").replace("&nbsp;"," ")
    soup = BeautifulSoup(data)
    dataTable = parseTable(str(soup.findAll('table',attrs={'id':'vatResponseFormTable'})))
    newtable = {}
    for dict1 in dataTable:
        if 'Name' in dict1:
            newtable['Name'] = dict1[1].strip() or ''
        if 'Address' in dict1:
            newtable['Address'] = dict1[1].strip() or ''
    return newtable

class res_partner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"
    
    name = fields.Char('Name', required=True, select=True, default=' ')        
    
    @api.one
    def button_get_partner_data(self):
        part = self[0]
        if part.vat:
            self.write({'vat': part.vat.upper().replace(" ","")})
        vat_number = vat_country = False
        if not vat_number and part.name:
            if len(part.name)>2:
                if part.name.upper()[:2]=='RO':
                        part.vat = part.name
                        self.write( {'vat': part.vat.upper().replace(" ","")}) 
        if part.vat:
            vat_country, vat_number = self._split_vat(part.vat)                
        if part.vat_subjected:
            self.write({'vat_subjected': False})

        if vat_number and vat_country:
            if vat_country.upper()=='RO':
                self.write({
                    'is_company': True,
                    'country_id': self.env['res.country'].search([('code','=','RO')])[0].id
                })
                res = requests.get('http://openapi.ro/api/companies/' + str(vat_number) + '.json')
                if res.status_code==200:
                    res = res.json()
                    state = False
                    if res['state']:
                        state = self.env['res.country.state'].search([('name','=',res['state'].title())])
                        if state:
                            state = state[0].id
                    self.write({
                        'name': res['name'].upper(),
                        'nrc': res['registration_id'] and res['registration_id'].upper() or '',
                        'street': res['address'].title(),
                        'street2': res['city'].title(),
                        'phone': res['phone'] and res['phone'] or '',
                        'fax': res['fax'] and res['fax'] or '',
                        'zip': res['zip'] and res['zip'].encode('utf-8') or '',
                        'vat_subjected': bool(res['vat'] == '1'),
                        'state_id': state,
                    })
                else:
                    result = getMfinDryscape(str(vat_number))
                    name = nrc = adresa = tel = fax = zip1 = vat_s = False
                    if 'Denumire platitor:' in result.keys():
                        name = result['Denumire platitor:'].upper()
                    if 'Adresa:' in result.keys():
                        adresa = result['Adresa:'] or ''
                    if 'Numar de inmatriculare la RegistrulComertului:' in result.keys():
                        nrc = result['Numar de inmatriculare la RegistrulComertului:']
                        if nrc == '-/-/-':
                            nrc = ''
                        else:
                            nrc = nrc.replace(' ', '')
                    if 'Codul postal:' in result.keys():
                        zip1 = result['Codul postal:'] or ''
                    if 'Judetul:' in result.keys():
                        state = False
                        jud = result['Judetul:'].title() or ''
                        if jud:
                            state = self.env['res.country.state'].search([('name','ilike',jud)])
                            if state:
                                state = state[0]
                    if 'Telefon:' in result.keys():
                        tel = result['Telefon:'] or ''
                    if 'Fax:' in dict1:
                        fax = result['Fax:'] or ''
                    if 'Taxa pe valoarea adaugata (data luarii in evidenta):' in result.keys():
                        vat_s = bool(result['Taxa pe valoarea adaugata (data luarii in evidenta):']<>'NU')
                    self.write({
                        'name': name or '',
                        'nrc': nrc or '',
                        'street': adresa or '',
                        'phone': tel or '',
                        'fax': fax or '',
                        'zip': zip1 or '',
                        'vat_subjected': vat_s or False,
                        'state_id': state,
                    })

            else:
                try:
                    dataTable = getViesData(vat_country.upper(), vat_number)
                    if dataTable:
                        if dataTable['Name'] and dataTable['Name']<>'---':
                            try:
                                self.write({'name': dataTable['Name'].decode('utf-8').upper(), 'is_company': True, 'vat_subjected':  True})
                            except:
                                self.write({'name': str_conv(dataTable['Name']).upper(), 'is_company': True, 'vat_subjected':  True})
                        if not part.street:
                            if dataTable['Address'] and dataTable['Address']<>'---':
                                try:
                                    self.write({'street': dataTable['Address'].decode('utf-8').title()})
                                except:
                                    self.write({'street': str_conv(dataTable['Address']).title()})
                        self.write({'vat_subjected': self.vies_vat_check(vat_country, vat_number)})
                except:
                    self.write({'vat_subjected': self.vies_vat_check(vat_country, vat_number)})
