# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Adrian Vasile <adrian.vasile@gmail.com>
#    Copyright (C) 2014 Adrian Vasile
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

class hr_advatages(models.Model):
    _name = 'hr.advantages'
    _description = 'Advantages'

    code = fields.Char(_('Code'), required = True, help = _('Advantage code'))
    name = fields.Char(_('Name'), required = True, help = _('Advantage name'))
    amount = fields.Float(_('Amount'), help = _('Advantage amount'))
    
class hr_contract_advantages(models.Model):
    _name = 'hr.contract.advantages'
    _description = 'Contract Advantages'

    @api.one
    @api.onchange('advantage')
    def _set_amount_default(self):
        if self.advantage.amount and self.amount is False:
            self.amount = self.advantage.amount

    contract_id = fields.Many2one(
        'hr.contract', _('Contract'), required = True)
    advantage = fields.Many2one(
        'hr.advantages', _('Advantage'), required = True)
    amount = fields.Float(_('Amount'), help = _('Advantage amount'))

class hr_contract(models.Model):
    _inherit = 'hr.contract'

    advantage_ids = fields.One2many(
        'hr.contract.advantages', 'contract_id', string="Advantages")
    programmer_or_handicaped = fields.Boolean(
        'Programmer or Handicaped', default = False)
