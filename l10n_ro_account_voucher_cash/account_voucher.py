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


from odoo import fields, models, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class account_bank_statement_line(models.Model):
    _name = "account.bank.statement.line"
    _inherit = "account.bank.statement.line"

    voucher_id = fields.Many2one('account.voucher', string='Voucher', ondelete='restrict')


class account_journal(models.Model):
    _name = "account.journal"
    _inherit = "account.journal"

    receipts_sequence_id = fields.Many2one('ir.sequence', string='Voucher Sequence',
                                           help="""This field contains the information related to the
            numbering of the vouchers (receipts) of this journal.""")


class account_voucher(models.Model):
    _name = 'account.voucher'
    _inherit = 'account.voucher'

    @api.multi
    def account_move_get(self):

        seq_obj = self.env['ir.sequence']
        voucher = self
        if not voucher.number and voucher.journal_id.type == 'cash':
            if voucher.type == 'receipt':
                if voucher.journal_id.receipts_sequence_id:
                    if not voucher.journal_id.receipts_sequence_id.active:
                        raise UserError(_('Please activate the receipts sequence of selected journal !'))

                    if not voucher.number:
                        number = voucher.journal_id.receipts_sequence_id.with_context(
                            {'fiscalyear_id': voucher.period_id.fiscalyear_id.id}).next_by_id()
                        self.write({'number': number, 'name': number})
                else:
                    raise UserError(_('Please define a receipts sequence on the journal.'))
            else:
                if voucher.reference:
                    self.write({'number': voucher.reference, 'name': voucher.reference})
            voucher.refresh()
        return super(account_voucher, self).account_move_get()

    @api.multi
    def action_move_line_create(self):
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        res = super(account_voucher, self).action_move_line_create()
        # Create line in cash statement for voucher posted in cash journals.
        statement_obj = self.env['account.bank.statement']
        statement_line_obj = self.env['account.bank.statement.line']

        for voucher in self:
            if voucher.journal_id.type == 'cash':
                bank_line = self.env['account.bank.statement.line'].search([('voucher_id', '=', voucher.id)])
                if not bank_line:
                    if voucher.type in ('sale', 'receipt'):
                        account_id = voucher.partner_id.property_account_receivable and voucher.partner_id.property_account_receivable.id
                        if not account_id:
                            account_id = voucher.company_id.property_customer_advance_account_id and voucher.company_id.property_customer_advance_account_id.id
                    else:
                        account_id = voucher.partner_id.property_account_payable and voucher.partner_id.property_account_payable.id
                        if not account_id:
                            account_id = voucher.company_id.property_supplier_advance_account_id and voucher.company_id.property_supplier_advance_account_id.id
                    statement = statement_obj.search(
                        [('journal_id', '=', voucher.journal_id.id), ('date', '=', voucher.date)], limit=1)
                    if not statement:
                        vals = {
                            'journal_id': voucher.journal_id.id,
                            'state': 'draft',
                            'date': voucher.date,
                        }
                        statement = statement_obj.create( vals)
                        #self.env['account.bank.statement'].onchange_journal_id([statement.id], voucher.journal_id.id)
                        statement._set_opening_balance(voucher.journal_id.id)
                        #self.env['account.bank.statement'].button_open([statement.id])
                        statement.button_open()

                    if statement.state != 'open':
                        raise UserError( _(
                            'The cash statement of journal %s from date is not in open state, please open it \n'
                            'to create the line in  it "%s".') % (voucher.journal_id.name, voucher.date))
                    args = {
                        'amount': voucher.type == 'receipt' and voucher.amount or -voucher.amount,
                        'date': voucher.date,
                        'name': str(voucher.number),
                        'account_id': account_id or False,
                        'partner_id': voucher.partner_id and voucher.partner_id.id or None,
                        'statement_id': statement.id,
                        'journal_id': statement.journal_id.id,
                        'ref': str(voucher.number),
                        'voucher_id': voucher.id,
                        'journal_entry_id': voucher.move_id.id,
                    }
                    statement_line_obj.create( args )
        return res

    @api.multi
    def cancel_voucher(self):
        reconcile_pool = self.env['account.move.reconcile']
        move_pool = self.env['account.move']
        move_line_pool = self.env['account.move.line']
        for voucher in self:
            # refresh to make sure you don't unlink an already removed move
            voucher.refresh()
            for line in voucher.move_ids:
                # refresh to make sure you don't unreconcile an already unreconciled entry
                line.refresh()
                if line.reconcile_partial_id:
                    move_lines = [move_line.id for move_line in line.reconcile_partial_id.line_partial_ids]
                    move_lines.remove(line.id)
                    line.reconcile_partial_id.unlink()
                    if len(move_lines) >= 2:
                        print "TODO reconcile_partial"

                        #move_line_pool.reconcile_partial(cr, uid, move_lines, 'auto', context=context)
                        move_lines.reconcile_partial('auto')
        return super(account_voucher, self).cancel_voucher()
