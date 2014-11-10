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

from datetime import datetime, date

from openerp import models, fields, api, _
from openerp.exceptions import Warning

import urllib
from zipfile import ZipFile
from StringIO import StringIO
import json
import requests

import psycopg2
import os, os.path

class res_partner_anaf(models.Model):
    _name = "res.partner.anaf"
    _description = "ANAF History about VAT on Payment"
    _order = "vat, operation_date DESC, end_date, start_date"
    
    
    vat = fields.Char('VAT')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    publish_date = fields.Date('Publish Date')
    operation_date = fields.Date('Operation Date')
    operation_type = fields.Selection([('I', 'Register'),
                                       ('E', 'Fix error'),
                                       ('D', 'Removal')],
                                      'Operation Type')
        
class res_partner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"    
        
    @api.one
    @api.depends('vat')
    def _compute_vat(self):
        self.vat_number = self.vat and self.vat[2:].replace(' ', '')
        
    @api.one
    @api.depends('vat_number')
    def _compute_anaf_history(self):
        history = self.env['res.partner.anaf'].search([('vat','=',self.vat_number)])
        if history:
            self.anaf_history = [(6, 0, [line.id for line in history])]
    
    vat_number = fields.Char('VAT', compute='_compute_vat')
    anaf_history = fields.One2many('res.partner.anaf', compute='_compute_anaf_history', string='ANAF History', readonly=True)
        
    # Grab VAT on Payment data from ANAF, update table - SQL injection 
    @api.model
    def _download_anaf_data(self):
        date = datetime.now()
        path = os.getcwd()
        print str(path)
        if os.path.exists(str(path) + "/istoric.txt"):
            t = os.path.getmtime(str(path) + "/istoric.txt")
            modify = datetime.fromtimestamp(t).strftime('%Y%m%d')        
        else:
            open(str(path) + "/istoric.txt", "w")
            modify = date.strftime('%Y%m%d')
        date = date.strftime('%Y%m%d')
        if modify<>date:
            url = urllib.urlopen('http://static.anaf.ro/static/10/Anaf/TVA_incasare/ultim_' + str(date) + '.zip')
            zipfile = ZipFile(StringIO(url.read()))
            zipfile.extractall(path=str(path))
    
            self._cr.execute(""" DELETE FROM res_partner_anaf """)
            self._cr.execute(""" COPY res_partner_anaf (id,vat,start_date, end_date, publish_date, operation_date, operation_type)
                         FROM '%s/istoric.txt' WITH DELIMITER '#' NULL '' """ % str(path))

    @api.multi
    def _check_vat_on_payment(self):
        ctx = dict(self._context)
        vat_on_payment = False
        if self.anaf_history:
            if len(self.anaf_history)>1 and ctx.get('check_date', False):
                lines = self.env['res.partner.anaf'].search([('id','in',[rec.id for rec in self.anaf_history]),('start_date','<=', ctx['check_date']),('end_date','>=',ctx['check_date'])])
                if lines and lines[0].operation_type == 'D':
                    vat_on_payment = True
            else:
                if self.anaf_history[0].operation_type == 'I':
                    vat_on_payment = True
        return vat_on_payment
                        
    @api.one
    def check_vat_on_payment(self):
        ctx = dict(self._context)
        ctx.update({'check_date': date.today()})
        self.vat_on_payment = self.with_context(ctx)._check_vat_on_payment()
        
    @api.multi
    def _check_vat_subjected(self):
        vat_s = vat_number = vat_country = False
        if self.vat:
            vat_country, vat_number = self.vat[:2].lower(), self.vat[2:].replace(' ', '')        
        if vat_number and vat_country and vat_country.upper()=='RO':
            res = requests.get('http://openapi.ro/api/companies/' + str(vat_number) + '.json')
            if res.status_code==200:
                res = json.loads(res.content)
                if res['vat']=='1':
                    vat_s = True
        return vat_s
        
    @api.one
    def check_vat_subjected(self):
        self.vat_subjected = self._check_vat_subjected()
    
    @api.multi
    def update_vat_one(self):
        self.check_vat_on_payment()
        self.check_vat_subjected()
    
    @api.one
    def button_get_partner_data(self):
        super(res.partner, self).button_get_partner_data()
        self.update_vat_one()
    
    @api.multi
    def update_vat_all(self):
        self._download_anaf_data()
        partners = self.search([('vat','!=',False)])        
        for partner in partners:
           partner.check_vat_on_payment()
           partner.check_vat_subjected()
    
    @api.model
    def _update_vat_all(self):
        self.update_vat_all()
