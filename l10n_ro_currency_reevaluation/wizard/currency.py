# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Fekete Mihai <mihai.fekete@forbiom.eu>
#    Copyright (C) 2014 FOREST AND BIOMASS SERVICES ROMANIA SA
#    (http://www.forbiom.eu).
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
from openerp.exceptions import except_orm

from datetime import datetime
from dateutil.relativedelta import relativedelta


class currency_reevaluation(models.TransientModel):
    _name = 'currency.reevaluation'

    period_id = fields.Many2one('account.period', 'Period',
                                help="The period to compute moves.",
                                required=True)
    journal_id = fields.Many2one('account.journal', 'Journal',
                                 help="The journal to post the entries.",
                                 required=True)
    company_id = fields.Many2one('res.company', 'Company',
                                 help="The company for which is the "
                                      "reevaluation.",
                                 required=True, change_default=True,
                                 default=lambda self: self.env['res.company'].
                                 _company_default_get('currency.reevaluation'))

    @api.one
    def compute_difference(self):

        form = self[0]
        move_obj = self.env['account.move']
        account_obj = self.env['account.account']
        journal_obj = self.env['account.journal']
        move_line_obj = self.env['account.move.line']
        curr_obj = self.env['res.currency']

        # get current period from company
        company = form.company_id
        period = form.period_id
        journal = form.journal_id

        company_currency = company.currency_id
        reevaluation_date = period.date_stop
        account_ids = [account.id for account in account_obj.search(
            [('currency_reevaluation', '=', True),
             ('company_id', '=', company.id)])]

        date1 = datetime.strptime(
            reevaluation_date, "%Y-%m-%d") + relativedelta(day=1, months=+1)

        ctx = dict(self._context)
        ctx1 = dict(self._context)
        ctx.update({'date': date1})

        expense_acc = company.expense_currency_exchange_account_id.id
        income_acc = company.income_currency_exchange_account_id.id

        # get account move lines with foreign currency posted before
        # reevaluation date (end of period)
        # balance and foreign balance are not taking in consideration newer
        # reconciliations
        reeval_lines = move_line_obj.search(
            [('state', '=', 'valid'),
             ('reconcile_id', '=', False),
             ('move_id.state', '=', 'posted'),
             ('company_id', '=', company.id),
             ('currency_id', '!=', False),
             ('account_id', 'in', account_ids),
             ('date', '<=', reevaluation_date),
             ('currency_reevaluation', '=', False)])

        created_ids = []
        if reeval_lines:
            vals = {'name': 'Currency update ' + period.code,
                    'journal_id': journal.id,
                    'period_id': period.id,
                    'date': period.date_stop}
            move_id = move_obj.create(vals)
            move = move_id[0]
            done = []
            for line in reeval_lines:
                if line.id not in done:
                    aml = line
                    currency = line.currency_id
                    account = line.account_id

                    balance = line.debit - line.credit
                    foreign_balance = line.amount_currency
                    if line.reconcile_partial_id:
                        rec_part = line.reconcile_partial_id.line_partial_ids
                        for rec_line in rec_part:
                            if rec_line.id != line.id:
                                if rec_line.date <= reevaluation_date:
                                    balance += rec_line.debit - rec_line.credit
                                    foreign_balance += rec_line.amount_currency
                                    done.append(rec_line.id)
                    if foreign_balance != 0.00:
                        new_amount = currency.with_context(ctx).compute(
                            foreign_balance, company_currency, round=True)
                        line_date = datetime.strptime(line.date, "%Y-%m-%d")
                        reval_date = datetime.strptime(reevaluation_date,
                                                       "%Y-%m-%d")

                        if (line_date.year == reval_date.year and
                                line_date.month == reval_date.month):
                            # get current currency rate
                            ctx1.update({'date': line_date})
                        else:
                            date1 = datetime.strptime(period.date_start,
                                                      "%Y-%m-%d")
                            ctx1.update({'date': date1})
                        old_amount = currency.with_context(ctx1).compute(
                             foreign_balance, company_currency, round=True)
                        amount = round(new_amount - old_amount, 2)
                        if amount != 0.00:
                            partner_id = line.partner_id.id
                            if amount > 0:
                                eval_account = income_acc
                                debit = abs(amount)
                                credit = 0.00
                            else:
                                eval_account = expense_acc
                                debit = 0.00
                                credit = abs(amount)

                            ref = 'Currency update ' + \
                                str(foreign_balance) + ' ' + \
                                str(currency.name) + \
                                ' ' + str(line.move_id.name)
                            valsm = {
                                'name': ref,
                                'ref': ref,
                                'move_id': move.id,
                                'journal_id': journal.id,
                                'account_id': account.id,
                                'partner_id': partner_id,
                                'period_id': period.id,
                                'debit': debit,
                                'credit': credit,
                                'currency_reevaluation': True,
                                'date': period.date_stop,
                            }
                            part_move = move_line_obj.create(valsm)
                            valsm = {
                                'name': ref,
                                'ref': ref,
                                'move_id': move.id,
                                'journal_id': journal.id,
                                'account_id': eval_account,
                                'partner_id': partner_id,
                                'period_id': period.id,
                                'debit': credit,
                                'credit': debit,
                                'date': period.date_stop,
                            }
                            move_line_obj.create(valsm)

                            move_lines_ids = [
                                move_line.id for move_line in
                                aml.reconcile_partial_id.line_partial_ids]
                            move_lines_ids.append(line.id)
                            move_lines_ids.append(part_move[0].id)
                            move_lines = move_line_obj.browse(move_lines_ids)
                            move_lines.reconcile_partial('auto')
                done.append(line.id)
            move.post()
            created_ids.append(move_id)

        lines = []
        curr_journals = self.env['account.journal'].search([
            ('currency', '!=', False)])
        if curr_journals:
            query = """
    SELECT DISTINCT ON (journal_id) j.id as journal_id, s.date AS date,
    s.balance_end_real as balance, c.id as currency_id
    FROM account_bank_statement s
    INNER JOIN account_journal j on s.journal_id = j.id
    INNER JOIN res_company com on s.company_id = com.id
    INNER JOIN res_currency c on (j.currency is not null and j.currency = c.id)
    INNER JOIN
    (SELECT journal_id, max(date) as max_date FROM account_bank_statement
    WHERE date <= %(reevaluation_date)s::date AND state = 'confirm'
    GROUP BY journal_id) d ON
    (s.journal_id = d.journal_id AND s.date = d.max_date)
    WHERE j.company_id = %(company_id)s AND j.id in %(journal_ids)s
    ORDER BY journal_id, date"""
            params = {
                'reevaluation_date': reevaluation_date,
                'company_id': company.id,
                'journal_ids': tuple(curr_journals.ids)}
            self._cr.execute(query, params)
            lines = self._cr.dictfetchall()
            for line in lines:
                currency = curr_obj.browse(line['currency_id'])
                journal = journal_obj.browse(line['journal_id'])

                new_amount = currency.with_context(ctx).compute(
                    line['balance'], company_currency, round=True)
                ctx1.update({'date': False,
                             'fiscalyear': period.fiscalyear_id.id,
                             'date_from': period.fiscalyear_id.date_start,
                             'date_to': period.date_stop})

                old_amount = journal.default_debit_account_id.with_context(
                    ctx1).read(['balance'])[0]['balance']
                amount = round(new_amount - old_amount, 2)
                if amount != 0.00:
                    vals = {'name': 'Currency update ' + period.code,
                            'journal_id': journal.id,
                            'period_id': period.id,
                            'date': period.date_stop}
                    move_id = move_obj.create(vals)
                    move = move_id[0]

                    if amount > 0:
                        eval_account = income_acc
                        journal_account = journal.default_debit_account_id
                        debit = abs(amount)
                        credit = 0.00
                    else:
                        eval_account = expense_acc
                        journal_account = journal.default_credit_account_id
                        debit = 0.00
                        credit = abs(amount)

                    valsm = {
                        'name': 'Currency update ' + str(line['balance']),
                        'ref': 'Currency update ' + str(line['balance']),
                        'move_id': move.id,
                        'journal_id': journal.id,
                        'account_id': journal_account.id,
                        'partner_id': False,
                        'period_id': period.id,
                        'debit': debit,
                        'credit': credit,
                        'amount_currency': 0.00,
                        'currency_id': currency.id,
                        'date': period.date_stop,
                    }
                    move_line_obj.create(valsm)
                    valsm = {
                        'name': 'Update ' + str(line['balance']),
                        'ref': 'Update ' + str(line['balance']),
                        'move_id': move.id,
                        'journal_id': journal.id,
                        'account_id': eval_account,
                        'partner_id': False,
                        'period_id': period.id,
                        'debit': credit,
                        'credit': debit,
                        'amount_currency': 0.00,
                        'currency_id': currency.id,
                        'date': period.date_stop,
                    }
                    move_line_obj.create(valsm)
                    created_ids.append(move_id)
                    move.post()
        if created_ids:
            return {'domain': "[('id','in', %s)]" % (created_ids,),
                    'name': _("Created reevaluation lines"),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'auto_search': True,
                    'res_model': 'account.move',
                    'view_id': False,
                    'search_view_id': False,
                    'type': 'ir.actions.act_window'}
        else:
            raise except_orm(
                _("Warning"), _("No accounting entry have been posted."))
