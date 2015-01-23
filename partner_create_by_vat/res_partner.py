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

from string import maketrans
import requests
from stdnum.eu.vat import check_vies
from lxml import html

from openerp import models, fields, api, _
from openerp.exceptions import Warning

CEDILLATRANS = maketrans(u'\u015f\u0163\u015e\u0162'.encode('utf8'), u'\u0219\u021b\u0218\u021a'.encode('utf8'))

def getMfinante(cod):
    headers = {
        "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)",
        "Content-Type": "multipart/form-data;"
    }
    params = {'cod': cod}
    res = requests.get('http://www.mfinante.ro/infocodfiscal.html', params = params, headers = headers)
    res.raise_for_status()

    htm = html.fromstring(res.text)
    table = htm.xpath("//div[@id='main']//center/table")[0] # sunt 2 tabele primul e important
    result = dict()
    for tr in table.iterchildren():
        key = ' '.join([x.strip() for x in tr.getchildren()[0].text_content().split('\n') if x.strip() != ''])
        val = ' '.join([x.strip() for x in tr.getchildren()[1].text_content().split('\n') if x.strip() != ''])
        result[key] = val.encode('utf8').translate(CEDILLATRANS).decode('utf8')
    return result

class res_partner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    name = fields.Char('Name', required=True, select=True, default=' ')

    @api.one
    def button_get_partner_data(self):
        part = self[0]
        vat = part.vat
        if vat:
            self.write({'vat': part.vat.upper().replace(" ","")})
        elif part.name and len(part.name.strip())>2 and part.name.strip().upper()[:2]=='RO' and part.name.strip()[2:].isdigit():
            part.vat = part.name.upper().replace(" ","")
            self.write( {'vat': part.vat})
        if not part.vat:
            raise Warning(_("No VAT number found"))

        vat_country, vat_number = self._split_vat(part.vat)                
 
        if part.vat_subjected:
            self.write({'vat_subjected': False})
        if vat_number and vat_country:
            self.write({
                'is_company': True,
                'country_id': self.env['res.country'].search([('code','ilike',vat_country)])[0].id
            })
            if vat_country == 'ro':
                try:
                    result = getMfinante(vat_number)
                    name = nrc = adresa = tel = fax = zip1 = vat_s = state = False
                    if 'Denumire platitor:' in result.keys():
                        name = result['Denumire platitor:'].upper()
                    if 'Adresa:' in result.keys():
                        adresa = result['Adresa:'].title() or ''
                    if 'Numar de inmatriculare la Registrul Comertului:' in result.keys():
                        nrc = result['Numar de inmatriculare la Registrul Comertului:']
                        if nrc == '-/-/-':
                            nrc = ''
                        else:
                            nrc = nrc.replace(' ', '')
                    if 'Codul postal:' in result.keys():
                        zip1 = result['Codul postal:'] or ''
                    if 'Judetul:' in result.keys():
                        jud = result['Judetul:'].title() or ''
                        if jud.lower().startswith('municip'):
                            jud = ' '.join(jud.split(' ')[1:])
                        if jud != '':
                            state = self.env['res.country.state'].search([('name','ilike',jud)])
                            if state:
                                state = state[0].id
                    if 'Telefon:' in result.keys():
                        tel = result['Telefon:'].replace('.', '') or ''
                    if 'Fax:' in result.keys():
                        fax = result['Fax:'].replace('.', '') or ''
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
                except:
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
                            'city': res['city'].title(),
                            'phone': res['phone'] and res['phone'] or '',
                            'fax': res['fax'] and res['fax'] or '',
                            'zip': res['zip'] and res['zip'].encode('utf-8') or '',
                            'vat_subjected': bool(res['vat'] == '1'),
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
