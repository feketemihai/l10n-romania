# Copyright (C) 2020 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_accounting_data_for_valuation(self):
        self = self.with_context(
            notice=self.picking_id.notice,
            sale=self.picking_id.picking_type_id.code == 'outgoing'
        )
        return super(StockMove, self)._get_accounting_data_for_valuation()