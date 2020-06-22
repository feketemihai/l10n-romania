# -*- coding: utf-8 -*-
# ©  2008-2020  Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class ProductCategory(models.Model):
    _inherit = 'product.category'


    @api.constrains('property_stock_valuation_account_id', 'property_stock_account_output_categ_id',
                    'property_stock_account_input_categ_id')
    def _check_valuation_accouts(self):
        # pentru Romania contul de evaluarea a stocului este egal cu cel intrare/iesire
        pass
