# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Tatár Attila
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

from openerp.osv.orm import Model, TransientModel
from openerp.osv import fields, osv
import requests
import datetime
import os
import tempfile
import zipfile
import logging

_logger = logging.getLogger(__name__)

class firms_vat_onp(Model):
    """
    List of firms with VAT on payment from static.anaf.ro
    """
    _name = 'firms.vatonp'
        
    _columns = {
            'nr_cui': fields.integer('Cod fiscal', select=True),
            'name': fields.char('Numele',size=128,select=True)
                }

class reg_changes(Model):
    """
    Changes in time to firms registry of VAT on payment at static.anaf.ro
    """
    _name = 'firms.vatonp.lines'
    _columns = {
                'firm_id': fields.many2one('firms.vatonp','Firma',select=True),
                'nr_cui': fields.integer('Cod fiscal', select=True),
                'date_from': fields.date('Data de la care aplica'),
                'date_to': fields.date('Data pana la care aplica'),
                'date_pub': fields.date('Data publicarii'),
                'updt_type': fields.char('Tipul actualizarii', size=1),
                } 

def _mkdir(newdir):
    """works the way a good mkdir should :)
        - already exists, silently complete
        - if exist regular file in the way, return false
        - parent directory(ies) does not exist, make them as well
        - from activestate.com recipe
    """
    _logger.warning('Current working dir: %s'%os.getcwd())
    if os.path.isdir(newdir):        
        return 'already exist'
    elif os.path.isfile(newdir):        
        return 'same file-name exist'
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            _mkdir(head)        
        if tail:            
            os.mkdir(newdir)
    return 'created'

class get_vatonp(TransientModel):
    """ 
    Class and method for get data from static.anaf.ro
    """
    
    _name = 'get_vatonp'

    def smart_get(self, cr, uid, context=None, mode='cron',f_name=''):

        def days_between(past, pres):
            """ past, pres - <type 'datetime.date'> """
            if (pres - past).days < 0 :
                pr = past
                pa = pres
            else:
                pa = past
                pr = pres
            numdays = (pr - pa).days
            res = [ past + datetime.timedelta(days=x) for x in range(0,numdays) ]    
            return res
        
        sconf_obj = self.pool.get('ir.config_parameter')
        conf_id_l = sconf_obj.search(cr,uid,[('key','=','vatonp_zip_path')])
        conf = {'value': os.environ['HOME']}
        if not conf_id_l:
            _logger.error("""VAT on payment zip data directory not set in System Parameters !!! 
                            Set it like: key - 'vatonp_zip_path',
                                         value - directory with access rights 
                            read, write, create to openerp user - user who started the server.
                                        Default: home dir of openerp user. """)
        else:
            conf = sconf_obj.read(cr, uid, conf_id_l[0],['key','value'])            
        result = _mkdir(conf['value'])
        if result in ['already exist','created']:
            os.chdir(conf['value'])
        elif result=='same file-name exist':
            _logger.error("   Same file-name exist like the data directory name set in System Parameters!!!")
            os.chdir(os.environ['HOME'])
            
        akt = datetime.datetime.now()+datetime.timedelta(hours=2)  #plus the difference from gmt to RO
        akt = akt.date()
        vatonp_obj = self.pool.get('firms.vatonp')
        vatonp_lines_obj = self.pool.get('firms.vatonp.lines')
        cr.execute('SELECT  max(create_date) from firms_vatonp;')        
        last_date = cr.fetchone()
        url_base = 'http://static.anaf.ro/static/10/Anaf/TVA_incasare/'
        if last_date[0]:                        
            last_date = datetime.datetime.strptime(last_date[0][:10],"%Y-%m-%d").date()            
            df_name_list = [str(dtm).replace('-','') for dtm in  days_between(last_date, akt)]
        else:
            df_name_list = ['ultim_' + str(akt).replace('-','')] 
        for df in df_name_list:
            url = url_base + df + '.zip'
            if mode =='cron':
                day_file_zip = requests.get(url)
                _logger.warning('Header from anaf.ro: %s'%day_file_zip.headers)                
                zip_name = df + '.zip'
                daily_file = open(zip_name,'wb')
                daily_file.write(day_file_zip.content)
                daily_file.close()
                with tempfile.NamedTemporaryFile(mode='r+w', dir='.',delete=True) as temp_file:
                    temp_file.write(day_file_zip.content)
                    temp_file.flush()
                    with zipfile.ZipFile(temp_file,'r') as tempfilezip:
                        with tempfilezip.open('agenti.txt') as temp_agenti:                 
                            for line in temp_agenti:
                                l = line.decode("windows-1252")
                                lu = l.encode("utf8")
                                lu = lu.strip()
                                cui,name = lu.split('#')
                                vatonp_obj.create(cr, uid, {'nr_cui':cui,'name':name})
                        cr.commit()
                        with tempfilezip.open('istoric.txt') as temp_istoric:
                            for line in temp_istoric:
                                l = line.strip()
                                regid,nr_cui,date_from,date_to,date_pub,date_act,act_type = l.split('#')
                                nr_cui=int(nr_cui)
                                if date_from:
                                    date_from = date_from[:4]+'-'+date_from[4:6]+'-'+date_from[6:]
                                else:
                                    date_from = None
                                if date_to:    
                                    date_to = date_to[:4]+'-'+date_to[4:6]+'-'+date_to[6:]
                                else:
                                    date_to = None
                                if date_pub:
                                    date_pub = date_pub[:4]+'-'+date_pub[4:6]+'-'+date_pub[6:]
                                else:
                                    date_pub = None
                                cr.execute('SELECT id,name FROM firms_vatonp WHERE nr_cui=%s',(nr_cui,))
                                f_data = cr.fetchone()
                                f_id = f_data and f_data[0]                                    
                                vatonp_lines_obj.create(cr, uid, {'firm_id':f_id,
                                                                  'nr_cui':nr_cui,
                                                                  'date_from':date_from,
                                                                  'date_to':date_to,
                                                                  'date_pub':date_pub,
                                                                  'updt_type':act_type,
                                                                  })
                        cr.commit()
        return True    