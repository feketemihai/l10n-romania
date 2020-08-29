# Copyright (C) 2020 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.tools import float_compare, float_round, float_is_zero


class StockMove(models.Model):
    _inherit = 'stock.valuation.layer'

    valued_type = fields.Char()


