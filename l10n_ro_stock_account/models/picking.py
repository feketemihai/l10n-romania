# -*- coding: utf-8 -*-
# ©  2008-201 9Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import AccessError, UserError



class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # se foloseste  la ....
    purchase_invoice_id = fields.Many2one('account.move', string='Purchase Bill')


