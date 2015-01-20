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

from stdnum.eu.vat import check_vies
import dryscrape
import requests

def getMfinDryscape(cod):
    import dryscrape

    sess = dryscrape.Session(base_url = 'http://www.mfinante.ro/')
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
                    name = nrc = adresa = tel = fax = zip1 = vat_s = state = False
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
                    result = check_vies(part.vat)
                    if result.name and result.name <> '---':
                        self.write({'name': unicode(result.name).upper(), 'is_company': True, 'vat_subjected':  True})
                    if not part.street and result.address and result.address <> '---':
                        self.write({'street': dataTable['Address'].decode('utf-8').title()})
                    self.write({'vat_subjected': result.valid})
                except:
                    self.write({'vat_subjected': self.vies_vat_check(vat_country, vat_number)})
