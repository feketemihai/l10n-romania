# Copyright (C) 2016 Forest and Biomass Romania
# Copyright (C) 2018 Dorin Hongu <dhongu(@)gmail(.)com
# Copyright (C) 2019 OdooERP Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models

class stock_move(models.Model):
    _name = "stock.move"
    _inherit = "stock.move"

    picking_type_code = fields.Selection(related='picking_type_id.code', string='Picking Type Code')