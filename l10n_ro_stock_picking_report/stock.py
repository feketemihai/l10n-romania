# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014 Deltatech All Rights Reserved
#                    Dorin Hongu <dhongu(@)gmail(.)com
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

from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _
from openerp.tools import config
import openerp.addons.decimal_precision as dp


class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    _columns = {
        'delegate_id': fields.many2one('res.partner', 'Delegate'),
        'mean_transp': fields.char('Mean transport', size=20, required=False),
    }

    def action_invoice_create(self, cr, uid, ids, journal_id=False, group=False, type='out_invoice', context=None):
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        context = context.copy()
        if type == 'out_invoice':
            for picking in self.browse(cr, uid, ids, context=context):
                # context['date_inv'] = picking.date
                context['default_delegate_id'] = picking.delegate_id.id
                context['default_mean_transp'] = picking.mean_transp

        res = super(stock_picking, self).action_invoice_create(
            cr, uid, ids, journal_id, group, type, context)

        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
