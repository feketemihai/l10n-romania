# -*- coding: utf-8 -*-
# ©  2008-2018 Fekete Mihai <mihai.fekete@forbiom.eu>
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models, _



class StockChangeStandardPrice(models.TransientModel):
    _inherit = "stock.change.standard.price"



    @api.model
    def default_get(self, fields):
        res = super(StockChangeStandardPrice, self).default_get(fields)
        product_or_template = self.env[self._context['active_model']].browse(self._context['active_id'])
        if 'counterpart_account_id' in fields :
            res['counterpart_account_id'] = product_or_template.property_account_creditor_price_difference.id or product_or_template.categ_id.property_account_creditor_price_difference_categ.id

        return res

