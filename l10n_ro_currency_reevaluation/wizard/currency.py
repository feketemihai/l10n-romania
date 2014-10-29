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

from openerp.osv import fields, osv
from openerp.tools.translate import _

import time
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

class currency_reevauluation(models.TransientModel):
	_name = 'currency.reevaluation'

	period_id = fields.Many2one('account.period','Period', help="The period to compute moves.", required=True)
	journal_id = fields.Many2one('account.journal','Journal', help="The journal to post the entries.", required=True)
	company_id = fields.Many2one('res.company','Company', help="The company for which is the reevaluation.", required=True)
    
    @api.one
	def get_lines(self, period_id, company_id):
	    lines = move_line_obj.search(cr, uid, [('state','=','valid'),('curr_act','=',False),('reconcile_id','=',False),('currency_id','!=',False),('amount_currency','!=',False),('account_id.user_type.code','in',('payable', 'receivable')),('date','<=',form.period_id.date_stop),('date','>=',form.period_id.date_start)])
		
	    query = ("SELECT l.id as id, l.account_id as account_id, l.partner_id, l.currency_id, "
                   "COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, "
                   "COALESCE(SUM(l.amount_currency), 0) as foreign_balance, "
                   " FROM account_move_line l "
                   " LEFT JOIN account_journal journal ON journal.id = l.journal_id"
                   " WHERE journal.type::text != ANY (ARRAY['cash'::character varying::text,'bank'::character varying::text])"
                   " l.account_id IN %(account_ids)s AND "
                   " l.period_id = %(period)s AND "
                   " l.currency_id IS NOT NULL AND "
                   " l.reconcile_id IS NULL AND "
                   " GROUP BY l.account_id, l.partner_id, l.currency_id")
        params = {'revaluation_date': revaluation_date,
                  'account_ids': tuple(ids)}
        return query, params
	
	def compute_difference(self, cr, uid, ids, context=None):
		
		context = context or {}
		form = self.browse(cr, uid, ids[0], context=context)
		move_obj = self.pool.get('account.move')
		account_obj = self.pool.get('account.account')
		journal_obj = self.pool.get('account.journal')
		move_line_obj = self.pool.get('account.move.line')
		period_obj = self.pool.get('account.period')
		user_obj = self.pool.get('res.users')
		curr_obj = self.pool.get('res.currency')

		company = user_obj.browse(cr, uid, uid).company_id

		# get current period from company
		period = form.period_id
		curr = company.currency_id
		
		#get receivable and payable accounts
		#get account move lines with foreign currency		
		lines = move_line_obj.search(cr, uid, [('state','=','valid'),('curr_act','=',False),('reconcile_id','=',False),('currency_id','!=',False),('amount_currency','!=',False),('account_id.user_type.code','in',('payable', 'receivable')),('date','<=',form.period_id.date_stop),('date','>=',form.period_id.date_start)])
		created_ids = []
		vals = {'name': 'Currency update '+period.code,
                'journal_id': form.journal_id.id,
                'period_id': period.id,
                'date':period.date_stop}            
		move_id = move_obj.create(cr, uid, vals, context=context)
		move = move_obj.browse(cr, uid, move_id)
		expense_acc = company.expense_currency_exchange_account_id.id
		income_acc = company.income_currency_exchange_account_id.id
		for line1 in lines:
			line = move_line_obj.browse(cr, uid, line1)
			part_move = False
			if line.journal_id.type in ('sale','purchase'):
				name, ref1, debit, credit, account_id, currency_id, partner_id = line.name, line.ref, line.debit, line.credit, line.account_id, line.currency_id, line.partner_id				
				if partner_id and account_id.user_type.code not in ('payable', 'receivable'):
					continue    
				if partner_id:
					amount_currency = line.amount_residual_currency
				else:
					amount_currency = line.amount_currency
				if ref1:
					ref = ref1
				elif name:
					ref = name
				else:
					ref = 'Currency update '+period.code
				date1 = datetime.strptime(form.period_id.date_stop,"%Y-%m-%d") + relativedelta(day=1, months=+1)
				ctx1 = context.copy()
				ctx1.update({'date': date1})                        
				amount1 = round(curr_obj._get_conversion_rate(cr, uid, currency_id, curr, ctx1) * abs(amount_currency),2)
				rec_ids = []
				if datetime.strptime(line.date,"%Y-%m-%d").month == datetime.strptime(form.period_id.date_start,"%Y-%m-%d").month:
					#get current currency rate
					date1 = datetime.strptime(line.date,"%Y-%m-%d")
					ctx1.update({'date': date1})                        
					amount2 = round(curr_obj._get_conversion_rate(cr, uid, currency_id, curr, ctx1) * abs(amount_currency),2)
					amount = round(amount1 - amount2,2)
				else:
					ctx2 = context.copy()				
					date2 = datetime.strptime(form.period_id.date_start,"%Y-%m-%d")
					ctx2.update({'date': date2})                        
					amount2 = round(curr_obj._get_conversion_rate(cr, uid, currency_id, curr, ctx2) * abs(amount_currency),2)	
					amount = round(amount1 - amount2,2)
				if amount <> 0.00:
					if account_id.user_type.code=='receivable':
						valsm = {
								'name':ref,
								'ref':ref,
								'move_id': move_id,
								'journal_id': form.journal_id.id,
								'account_id': account_id.id,
								'partner_id': partner_id.id,
								'period_id': period.id,
								'debit': amount>0 and abs(amount) or 0.00,
								'credit': amount<0 and abs(amount) or 0.00,
								'currency_id': currency_id.id,
								'curr_act':True,
								'date':period.date_stop,
						}
						part_move = move_line_obj.create(cr, uid, valsm)
						valsm = {
								'name':ref,
								'ref':ref,
								'move_id': move_id,
								'journal_id': form.journal_id.id,
								'account_id': amount>0 and income_acc or expense_acc,
								'partner_id': False,
								'period_id': period.id,
								'debit': amount<0 and abs(amount) or 0.00,
								'credit': amount>0 and abs(amount) or 0.00,
								'currency_id': currency_id.id,
								'curr_act':True,
								'date':period.date_stop,
						}
						move_line_obj.create(cr, uid, valsm)
					else:
						valsm = {
								'name':ref,
								'move_id': move_id,
								'journal_id': form.journal_id.id,
								'account_id': account_id.id,
								'partner_id': partner_id.id,
								'period_id': period.id,
								'debit': amount<0 and abs(amount) or 0.00,
								'credit': amount>0 and abs(amount) or 0.00,
								'currency_id': currency_id.id,
								'curr_act':True,
								'date':period.date_stop,
						}
						part_move = move_line_obj.create(cr, uid, valsm)
						valsm = {
								'name':ref,
								'move_id': move_id,
								'journal_id': form.journal_id.id,
								'account_id': amount>0 and expense_acc or income_acc ,
								'partner_id': False,
								'period_id': period.id,
								'debit': amount>0 and abs(amount) or 0.00,
								'credit': amount<0 and abs(amount) or 0.00,
								'currency_id': currency_id.id,
								'curr_act':True,
								'date':period.date_stop,
						}
						move_line_obj.create(cr, uid, valsm)
				if part_move:
					move_line_obj.reconcile_partial(cr, uid, [line.id, part_move], writeoff_acc_id=account_id.id, writeoff_period_id=period.id, writeoff_journal_id=form.journal_id.id)                
		year, month, day = (int(x) for x in form.period_id.date_stop.split('-'))
		start_date = date(year, month, day)
		lines = []
		cr.execute('SELECT DISTINCT ON (journal) j.id as journal, s.date AS date, j.code as code, s.balance_end_real as balance, c.id as currency ' \
                       'FROM account_bank_statement s ' \
                       'INNER JOIN account_journal j on s.journal_id = j.id ' \
                       'INNER JOIN res_company com on s.company_id = com.id ' \
                       'INNER JOIN res_currency c on ((j.currency is not null and j.currency = c.id))' \
                       'INNER JOIN ' \
                           '(SELECT journal_id, max(date) as max_date FROM account_bank_statement ' \
                               'WHERE date <= \'%s\' ' \
                               'GROUP BY journal_id) d ' \
                               'ON (s.journal_id = d.journal_id AND s.date = d.max_date) ' \
                       'ORDER BY journal, code, date' % start_date)
		lines = cr.dictfetchall()
		for line in lines:
			ref = str(journal_obj.browse(cr, uid, line['journal']).name)
			ctx1 = context.copy()
			date1 = datetime.strptime(form.period_id.date_stop,"%Y-%m-%d") + relativedelta(day=1, months=+1)
			ctx1.update({'date': date1})                        
			new_rate = str(round(curr_obj._get_conversion_rate(cr, uid, curr_obj.browse(cr, uid, line['currency']), curr, ctx1),4))
			cr.execute('SELECT s.date AS date, s.balance_start as balance_start, s.total_entry_encoding as balance ' \
                       'FROM account_bank_statement s ' \
                       'INNER JOIN account_journal j on s.journal_id = j.id ' \
                       'WHERE journal_id = \'%s\'  AND period_id = \'%s\' ' \
                       'ORDER BY date' % (line['journal'], period.id))
			oldlines = cr.dictfetchall()
			amount = 0.00
			ctx2 = context.copy()
			if oldlines:
				for bank_line in oldlines:
					if bank_line == oldlines[0]:
						amount1 = round(curr_obj.compute(cr, uid, line['currency'], curr.id, bank_line['balance_start'], context=ctx1),2)
						date2 = datetime.strptime(form.period_id.date_start,"%Y-%m-%d")
						ctx2.update({'date': date2})                        
						amount2 = round(curr_obj.compute(cr, uid, line['currency'], curr.id, bank_line['balance_start'], context=ctx2),2)
						amount += amount1-amount2
					amount1 = round(curr_obj.compute(cr, uid, line['currency'], curr.id, bank_line['balance'], context=ctx1),2)
					date2 = bank_line['date']
					ctx2.update({'date': date2})                        
					amount2 = round(curr_obj.compute(cr, uid, line['currency'], curr.id, bank_line['balance'], context=ctx2),2)
					amount += amount1-amount2				
			else:
				amount1 = round(curr_obj.compute(cr, uid, line['currency'], curr.id, line['balance'], context=ctx1),2)
				date2 = datetime.strptime(form.period_id.date_start,"%Y-%m-%d")
				ctx2.update({'date': date2})                        
				amount2 = round(curr_obj.compute(cr, uid, line['currency'], curr.id, line['balance'], context=ctx2),2)
				print line
				print str(amount1-amount2)
				amount += amount1-amount2
			if amount <> 0.00:
				valsm = {
						'name': 'Update ' + str(line['balance']) + ' from ' + ref + ' at ' + new_rate,
						'move_id': move_id,
						'journal_id': form.journal_id.id,
						'account_id': amount>0 and (journal_obj.browse(cr, uid, line['journal']).default_credit_account_id and journal_obj.browse(cr, uid, line['journal']).default_credit_account_id.id) or (journal_obj.browse(cr, uid, line['journal']).default_debit_account_id and journal_obj.browse(cr, uid, line['journal']).default_debit_account_id.id),
						'period_id': period.id,
						'partner_id': False,
						'debit': amount>0 and abs(amount) or 0.00,
						'credit': amount<0 and abs(amount) or 0.00,
						'curr_act':True,
						'date':period.date_stop,
				}
				move_line_obj.create(cr, uid, valsm)
				valsm = {
						'name':'Update ' + str(line['balance']) + ' from ' + ref + ' at ' + new_rate,
						'move_id': move_id,
						'journal_id': form.journal_id.id,
						'account_id': amount>0 and income_acc or expense_acc,
						'period_id': period.id,
						'partner_id': False,
						'debit': amount<0 and abs(amount) or 0.00,
						'credit': amount>0 and abs(amount) or 0.00,
						'curr_act':True,
						'date':period.date_stop,
				}
				move_line_obj.create(cr, uid, valsm)
						
					
		created_ids.append(move_id)
		if created_ids:
			return {'domain': "[('id','in', %s)]" % (created_ids,),
				'name': _("Created revaluation lines"),
				'view_type': 'form',
				'view_mode': 'tree,form',
				'auto_search': True,
				'res_model': 'account.move',
				'view_id': False,
				'search_view_id': False,
				'type': 'ir.actions.act_window'}
		else:
			raise osv.except_osv(_("Warning"), _("No accounting entry have been posted."))
			
CurrencyDifference()
